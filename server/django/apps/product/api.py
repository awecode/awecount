from datetime import datetime
from openpyxl import load_workbook

from django.db import IntegrityError
from django.db import transaction
from django.conf import settings
from django.db.models import Sum, Q
from django_filters import rest_framework as filters
from rest_framework import filters as rf_filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FileUploadParser

from apps.ledger.models import Account, Category as AccountCategory
from apps.ledger.serializers import AccountMinSerializer
from apps.tax.models import TaxScheme
from apps.tax.serializers import TaxSchemeMinSerializer
from apps.voucher.models import ChallanRow, CreditNoteRow, DebitNoteRow, PurchaseOrderRow, PurchaseVoucher, PurchaseVoucherRow, SalesVoucherRow
from awecount.libs.CustomViewSet import CRULViewSet, GenericSerializer
from awecount.libs.mixins import InputChoiceMixin, ShortNameChoiceMixin
from .filters import ItemFilterSet, BookFilterSet, InventoryAccountFilterSet
from .models import Category as InventoryCategory, InventoryAccount
from .models import Item, JournalEntry, Category, Brand, Unit, Transaction
from .serializers import ItemListMinSerializer, ItemSerializer, UnitSerializer, InventoryCategorySerializer, BrandSerializer, \
    ItemDetailSerializer, InventoryAccountSerializer, JournalEntrySerializer, BookSerializer, \
    TransactionEntrySerializer, \
    ItemPOSSerializer, ItemListSerializer, ItemOpeningSerializer, InventoryCategoryTrialBalanceSerializer


class ItemViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = ItemSerializer
    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ['name', 'code', 'description', 'search_data', 'selling_price', 'cost_price', ]
    filterset_class = ItemFilterSet
    parser_classes = [JSONParser, MultiPartParser]

    collections = (
        ('brands', Brand, BrandSerializer),
        ('inventory_categories', InventoryCategory, InventoryCategorySerializer),
        ('units', Unit, UnitSerializer),
        ('purchase_accounts', Account.objects.filter(category__name="Purchase"), AccountMinSerializer),
        ('sales_accounts', Account.objects.filter(category__name="Sales"), AccountMinSerializer),
        ('tax_scheme', TaxScheme, TaxSchemeMinSerializer),
        ('discount_allowed_accounts', Account.objects.filter(category__name='Discount Expenses'), AccountMinSerializer),
        ('discount_received_accounts', Account.objects.filter(category__name='Discount Income'), AccountMinSerializer)
    )

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.order_by('-id')
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ItemListSerializer
        if self.action == 'list_items':
            return ItemListMinSerializer
        return self.serializer_class
    
    def merge_items(self, item_ids, config=None):
        items = Item.objects.filter(id__in=item_ids)
        for i in range(len(items)-1):
            item1 = items[i]
            item2 = items[i+1]
            if ((item1.can_be_purchased or item1.can_be_sold or item1.fixed_asset) and (item2.direct_expense or item2.indirect_expense)) or ((item2.can_be_purchased or item2.can_be_sold or item2.fixed_asset) and (item1.direct_expense or item1.indirect_expense)):
                return True

        # Select one item from the items list
        if config and config.get("defaultItem"):
            item = items.get(id=config["defaultItem"])
        else:
            item = items[0]

        remaining_items = items.exclude(id = item.id)

        # Set the selected item in purchase rows, sales rows, challan rows, purchase order rows, debit_rows and credit rows
        purchase_voucher_rows = PurchaseVoucherRow.objects.filter(item__id__in=item_ids)
        purchase_voucher_rows.update(item=item)

        sales_voucher_rows = SalesVoucherRow.objects.filter(item__id__in=item_ids)
        sales_voucher_rows.update(item=item)

        challan_rows = ChallanRow.objects.filter(item__id__in=item_ids)
        challan_rows.update(item=item)

        purchase_order_rows = PurchaseOrderRow.objects.filter(item__id__in=item_ids)
        purchase_order_rows.update(item=item)

        credit_note_rows = CreditNoteRow.objects.filter(item__id__in=item_ids)
        credit_note_rows.update(item=item)

        debit_note_rows = DebitNoteRow.objects.filter(item__id__in=item_ids)
        debit_note_rows.update(item=item)

        # Update Inventory account for inventory transactions
        if not item.track_inventory:
            item.track_inventory = True
        inventory_account = InventoryAccount.objects.get_or_create(company=item.company, code=item.code, name=self.name)[0]

        names = [x.name for x in remaining_items]
        remaining_items_inventory_accounts = InventoryAccount.objects.filter(name__in=names, company=item.company)
        inventory_transactions = Transaction.objects.filter(account__in=remaining_items_inventory_accounts)
        inventory_transactions.update(account=inventory_account)

        # Delete other items
        remaining_items = items.exclude(id=item.id)
        remaining_items.delete()
        return False
    
    @action(detail=False, url_path="list")
    def list_items(self, request):
        qs = super().get_queryset().order_by("name")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, url_path='similar-items')
    def similar_items(self, request):
        from thefuzz import fuzz
        qs = super().get_queryset()
        items = qs.values_list('id', 'name', 'code')
        res = []
        for item in items:
            obj = {}
            similar_items = []
            for id, name, code in items:
                if fuzz.ratio(item[1], name)>80:
                    similar_items.append({
                        "id": id,
                        "name": f"{name} ({code})",
                        "code": code,
                        # "match": fuzz.ratio(item[1], name)
                    })
            if len(similar_items)>1:
                obj['items'] = similar_items
                obj['config'] = {}
                # res[item[1]] = sim
                res.append(obj)

        unique_ids = {}

        # Filter out duplicate items
        filtered_data = []
        for group in res:
            unique_items = []
            for item in group["items"]:
                item_id = item["id"]
                if item_id not in unique_ids:
                    unique_ids[item_id] = True
                    unique_items.append(item)
            if unique_items:
                filtered_data.append({"items": [x["id"] for x in unique_items], "config": group["config"]})

        return Response(filtered_data)

    @action(detail=False, methods=['POST'])
    def merge(self, request):
        groups_not_merged = []
        items_not_merged = []
        flag = False
        for index, group in enumerate(request.data):
            if group.get("config"):
                ret = self.merge_items(group["items"], group["config"])
            else:
                ret = self.merge_items(group["items"])
            if ret:
                flag = True
                groups_not_merged.append(index+1)
                for item in group["items"]:
                    items_not_merged.append(item)
        if flag:
            res = {
                "error": {
                    "message" : f"Items in Groups {','.join([str(x) for x in groups_not_merged])} were not merged due to conflicting config on items.",
                    "items": items_not_merged
                } 
            }
            return Response(res, status=209)
        return Response(status=200)

    @action(detail=True)
    def details(self, request, pk=None):
        qs = super().get_queryset().select_related('account', 'sales_account', 'purchase_account', 'discount_allowed_account',
                                                   'discount_received_account', 'expense_account', 'fixed_asset_account',
                                                   'tax_scheme')
        item = get_object_or_404(queryset=qs, pk=pk)
        serializer = ItemDetailSerializer(item, context={'request': request}).data
        return Response(serializer)

    # items listing for POS
    @action(detail=False)
    def pos(self, request):
        self.filter_backends = (rf_filters.SearchFilter,)
        self.queryset = self.get_queryset().filter(can_be_sold=True)
        self.serializer_class = ItemPOSSerializer
        self.search_fields = ['name', 'code', 'description', 'search_data', ]
        self.paginator.page_size = settings.POS_ITEMS_SIZE
        return super().list(request)

    @action(detail=False, url_path='sales-choices')
    def sales_choices(self, request):
        queryset = self.get_queryset().filter(can_be_sold=True)
        serializer = GenericSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["POST"], url_path="import")
    def import_from_file(self, request):
        file = request.FILES["file"]
        wb = load_workbook(file)
        ws = wb.active
        ws.delete_rows(1)
        items = []

        def get_bool_for_txt(value):
            if not value:
                return False
            elif value.upper()=="F":
                return False
            elif value.upper()=="T":
                return True
            else:
                raise ValueError("Invalid value detected.")
            
        def get_category(value):
            if not value:
                return None
            else:
                qs = Category.objects.filter(name__iexact=value, company_id=request.company.id)
                if qs.exists():
                    return qs.first()
                else:
                    if request.data.get("create_new_category") == "true":
                        cat = Category.objects.create(name=value, company_id=request.company.id)
                        return cat
                    return None
                    
            
        for row in ws.iter_rows(values_only=True):
            item = {
                "company_id":request.company.id,
                "name":row[0],
                "code":row[1],
                "category":get_category(row[2]),
                "cost_price":row[3],
                "selling_price":row[4],
                "can_be_purchased":get_bool_for_txt(row[5]),
                "can_be_sold":get_bool_for_txt(row[6]),
                "track_inventory":False
            }
            item_obj = Item(**item)
            items.append(item_obj)

        with transaction.atomic():
            try:
                Item.objects.bulk_create(items, batch_size=1000)
                # items = Item.objects.bulk_create(items)
                accounts_to_create = []
                items_to_update = []
                for i, item in enumerate(items):
                    # print(i)
                    if item.can_be_purchased:
                        name = item.name + ' (Purchase)'
                        purchase_account = Account(name=name, company=item.company)
                        purchase_account.add_category('Purchase')
                        purchase_account.suggest_code(item)
                        accounts_to_create.append(purchase_account)
                        item.purchase_account = purchase_account

                        name = 'Discount Received - ' + item.name
                        discount_received_acc = Account(name=name, company=item.company)
                        discount_received_acc.add_category('Discount Income')
                        discount_received_acc.suggest_code(item)
                        accounts_to_create.append(discount_received_acc)
                        item.discount_received_account = discount_received_acc

                    if item.can_be_sold:
                        name = item.name + ' (Sales)'
                        sales_account = Account(name=name, company=item.company)
                        sales_account.add_category('Sales')
                        sales_account.suggest_code(item)
                        accounts_to_create.append(sales_account)
                        item.sales_account = sales_account

                        name = 'Discount Allowed - ' + item.name
                        discount_allowed_account = Account(name=name, company=item.company)
                        discount_allowed_account.add_category('Discount Expenses')
                        discount_allowed_account.suggest_code(item)
                        accounts_to_create.append(discount_allowed_account)
                        item.discount_allowed_account = discount_allowed_account

                    items_to_update.append(item)

                Account.objects.bulk_create(accounts_to_create, batch_size=1000)
                Item.objects.bulk_update(items_to_update, fields=["purchase_account", "sales_account", "discount_received_account", "discount_allowed_account"])

            except IntegrityError as e:
                code = e.args[0].split("=(")[1].split(")")[0].split(",")[0]
                res_msg = f"Duplicate items with code {code} detected."
                return Response({"details": res_msg}, status=400)        
        return Response({}, status=200)


class ItemOpeningBalanceViewSet(CRULViewSet):
    serializer_class = ItemOpeningSerializer
    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ['item__name', 'item__code', 'item__description', 'item__search_data', 'opening_balance', ]
    filterset_class = InventoryAccountFilterSet

    collections = (
        ('items', Item.objects.filter(track_inventory=True, account__opening_balance=0), ItemListSerializer),
    )

    def get_queryset(self, company_id=None):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.filter(opening_balance__gt=0)
        return qs

    def get_update_defaults(self, request=None):
        self.collections = (
            ('items', Item.objects.filter(track_inventory=True).filter(
                Q(account__opening_balance=0) | Q(account_id=self.kwargs.get('pk'))), ItemListSerializer),
        )
        return self.get_defaults(request=request)

    def create(self, request, *args, **kwargs):
        data = request.data
        account = get_object_or_404(InventoryAccount, item__id=data.get('item_id'), opening_balance=0, company=request.company)
        account.opening_balance = data.get('opening_balance')
        account.save()
        fiscal_year = self.request.company.current_fiscal_year
        account.item.update_opening_balance(fiscal_year)
        return Response({})

    def perform_update(self, serializer):
        super().perform_update(serializer)
        fiscal_year = self.request.company.current_fiscal_year
        serializer.instance.item.update_opening_balance(fiscal_year)


class BookViewSet(InputChoiceMixin, CRULViewSet):
    collections = (
        ('brands', Brand, BrandSerializer),
    )

    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ['name', 'code', 'description', 'search_data', 'selling_price', 'cost_price', ]
    filterset_class = BookFilterSet

    def get_queryset(self, **kwargs):
        queryset = Item.objects.filter(category__name="Book", company=self.request.company)
        return queryset

    serializer_class = BookSerializer

    @action(detail=False)
    def category(self, request):
        cat = Category.objects.filter(company=self.request.company, name="Book").first()
        return Response(InventoryCategorySerializer(cat).data)


class UnitViewSet(InputChoiceMixin, ShortNameChoiceMixin, CRULViewSet):
    serializer_class = UnitSerializer


class InventoryCategoryViewSet(InputChoiceMixin, ShortNameChoiceMixin, CRULViewSet):
    serializer_class = InventoryCategorySerializer
    collections = (
        ('units', Unit, UnitSerializer),
        ('accounts', Account, AccountMinSerializer),
        ('tax_scheme', TaxScheme, TaxSchemeMinSerializer),
        ('discount_allowed_accounts', Account.objects.filter(category__name='Discount Expenses'), AccountMinSerializer),
        ('discount_received_accounts', Account.objects.filter(category__name='Discount Income'), AccountMinSerializer),
    )

    def get_collections(self, request=None):
        collections_data = super().get_collections(self.request)
        collections_data['fixed_assets_categories'] = GenericSerializer(
            AccountCategory.objects.get(name='Fixed Assets', default=True, company=self.request.company).get_descendants(
                include_self=True), many=True).data
        collections_data['direct_expenses_categories'] = GenericSerializer(
            AccountCategory.objects.get(name='Direct Expenses', default=True, company=self.request.company).get_descendants(
                include_self=True), many=True).data
        collections_data['indirect_expenses_categories'] = GenericSerializer(
            AccountCategory.objects.get(name='Indirect Expenses', default=True, company=self.request.company).get_descendants(
                include_self=True), many=True).data
        return collections_data

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.order_by('-id')
        return qs

    @action(detail=False, url_path='trial-balance')
    def trial_balance(self, request):
        qs = self.get_queryset().filter(Q(track_inventory=True) | Q(fixed_asset=True))
        return Response(InventoryCategoryTrialBalanceSerializer(qs, many=True).data)


class BrandViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = BrandSerializer


class InventoryAccountViewSet(InputChoiceMixin, CRULViewSet):
    serializer_class = InventoryAccountSerializer

    filter_backends = (filters.DjangoFilterBackend, rf_filters.OrderingFilter, rf_filters.SearchFilter)
    search_fields = ('code', 'name',)

    def get_account_ids(self, obj):
        return [obj.id]

    @action(detail=True, methods=['get'], url_path='journal-entries')
    def journal_entries(self, request, pk=None):

        param = request.GET
        start_date = param.get('start_date')
        end_date = param.get('end_date')
        obj = self.get_object()
        entries = JournalEntry.objects.filter(transactions__account_id=obj.pk).order_by('pk',
                                                                                        'date') \
            .prefetch_related('transactions', 'content_type', 'transactions__account').select_related()

        if start_date or end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            if start_date == end_date:
                entries = entries.filter(date=start_date)
            else:
                entries = entries.filter(date__range=[start_date, end_date])
        serializer = JournalEntrySerializer(entries, context={'account': obj}, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        param = request.GET
        obj = self.get_object()
        serializer_class = self.get_serializer_class()
        data = serializer_class(obj).data
        account_ids = self.get_account_ids(obj)
        start_date = param.get('start_date', None)
        end_date = param.get('end_date', None)
        transactions = Transaction.objects.filter(account_id__in=account_ids).order_by('-journal_entry__date', '-pk') \
            .select_related('journal_entry__content_type')

        aggregate = {}
        if start_date or end_date:
            if start_date == 'null':
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Either start date or both dates are required to filter.")
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            # TODO: if only start date is given, raise error or process some other way?
            end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date != 'null' else datetime.today()
            if start_date == end_date:
                transactions = transactions.filter(journal_entry__date=start_date)
            else:
                transactions = transactions.filter(journal_entry__date__range=[start_date, end_date])
            aggregate = transactions.aggregate(Sum('dr_amount'), Sum('cr_amount'))

        # Only show 5 because fetching voucher_no is expensive because of GFK, GFK to be cached
        # self.paginator.page_size = 5
        page = self.paginate_queryset(transactions)
        serializer = TransactionEntrySerializer(page, many=True)
        data['transactions'] = self.paginator.get_response_data(serializer.data)
        data['aggregate'] = aggregate
        return Response(data)

    @action(detail=False, url_path='trial-balance')
    def trial_balance(self, request, format=None):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            qq = InventoryAccount.objects.filter(company=request.company).annotate(
                od=Sum('transactions__dr_amount', filter=Q(transactions__journal_entry__date__lt=start_date)),
                oc=Sum('transactions__cr_amount', filter=Q(transactions__journal_entry__date__lt=start_date)),
                cd=Sum('transactions__dr_amount', filter=Q(transactions__journal_entry__date__lte=end_date)),
                cc=Sum('transactions__cr_amount', filter=Q(transactions__journal_entry__date__lte=end_date)),
            ) \
                .values('id', 'name', 'item__category_id', 'od', 'oc', 'cd', 'cc').exclude(od=None, oc=None, cd=None, cc=None)
            return Response(list(qq))
        return Response({})
