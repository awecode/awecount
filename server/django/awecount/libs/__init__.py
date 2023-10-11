import os
import re

from decimal import Decimal
from django.db import connection
from django.conf import settings

from django.contrib.contenttypes.models import ContentType


def get_next_voucher_no(cls, company_id, attr='voucher_no'):
    from django.db.models import Max

    qs = cls.objects.all()
    if company_id:
        qs = qs.filter(company_id=company_id)

    # Check if the voucher number needs to be unique by fiscal year
    for unique_tuple in cls._meta.unique_together:
        if attr in unique_tuple and 'fiscal_year' in unique_tuple:
            qs = qs.filter(fiscal_year__companies=company_id)
            break

    max_voucher_no = qs.aggregate(Max(attr))[attr + '__max']
    if max_voucher_no:
        return int(max_voucher_no) + 1
    else:
        return 1


def zero_for_none(obj):
    if obj is None or obj == '':
        return 0
    else:
        return obj


def decimalize(obj):
    if obj is None or obj == '':
        return Decimal(0)
    else:
        return Decimal(str(obj))


def none_for_zero(obj):
    if not obj:
        return None
    else:
        return obj


def model_exists_in_db(model):
    return model._meta.db_table in connection.introspection.table_names()


def delete_rows(rows, model):
    if rows:
        from apps.ledger.models import JournalEntry
        from apps.product.models import JournalEntry as InventoryJournalEntry
        # Assuming all rows have the same content type, find content type only once
        content_type = None
        row_ids = []
        for row in rows:
            if row.get('id'):
                instance = model.objects.get(id=row.get('id'))
                if not content_type:
                    content_type = ContentType.objects.get_for_model(instance)
                instance.delete()
                row_ids.append(row.get('id'))

        JournalEntry.objects.filter(content_type=content_type, object_id__in=row_ids).delete()
        InventoryJournalEntry.objects.filter(content_type=content_type, object_id__in=row_ids).delete()


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = settings.STATIC_URL  # Typically /static/
    sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL  # Typically /static/media/
    mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


class Number2Words(object):
    def __init__(self):
        '''Initialise the class with useful data'''

        self.wordsDict = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven',
                          8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen',
                          14: 'fourteen', 15: 'fifteen', 16: 'sixteen', 17: 'seventeen',
                          18: 'eighteen', 19: 'nineteen', 20: 'twenty', 30: 'thirty', 40: 'forty',
                          50: 'fifty', 60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'ninty'}

        self.powerNameList = ['thousand', 'lakh', 'crore']

    def convertNumberToWords(self, number):

        # Check if there is decimal in the number. If Yes process them as paisa part.
        formString = str(number)
        if formString.find('.') != -1:
            withoutDecimal, decimalPart = formString.split('.')

            paisaPart = str(round(float(formString), 2)).split('.')[1]
            inPaisa = self._formulateDoubleDigitWords(paisaPart)

            formString, formNumber = str(withoutDecimal), int(withoutDecimal)
        else:
            # Process the number part without decimal separately
            formNumber = int(number)
            inPaisa = None

        if not formNumber:
            return 'zero'

        self._validateNumber(formString, formNumber)

        inRupees = self._convertNumberToWords(formString)

        if inPaisa:
            return '%s and %s paisa' % (inRupees.title(), inPaisa.title())
        else:
            return '%s' % inRupees.title()

    def _validateNumber(self, formString, formNumber):

        assert formString.isdigit()

        # Developed to provide words upto 999999999
        if formNumber > 999999999 or formNumber < 0:
            raise AssertionError('Out Of range')

    def _convertNumberToWords(self, formString):

        MSBs, hundredthPlace, teens = self._getGroupOfNumbers(formString)

        wordsList = self._convertGroupsToWords(MSBs, hundredthPlace, teens)

        return ' '.join(wordsList)

    def _getGroupOfNumbers(self, formString):

        hundredthPlace, teens = formString[-3:-2], formString[-2:]

        msbUnformattedList = list(formString[:-3])

        # ---------------------------------------------------------------------#

        MSBs = []
        tempstr = ''
        for num in msbUnformattedList[::-1]:
            tempstr = '%s%s' % (num, tempstr)
            if len(tempstr) == 2:
                MSBs.insert(0, tempstr)
                tempstr = ''
        if tempstr:
            MSBs.insert(0, tempstr)

        # ---------------------------------------------------------------------#

        return MSBs, hundredthPlace, teens

    def _convertGroupsToWords(self, MSBs, hundredthPlace, teens):

        wordList = []

        # ---------------------------------------------------------------------#
        if teens:
            teens = int(teens)
            tensUnitsInWords = self._formulateDoubleDigitWords(teens)
            if tensUnitsInWords:
                wordList.insert(0, tensUnitsInWords)

        # ---------------------------------------------------------------------#
        if hundredthPlace:
            hundredthPlace = int(hundredthPlace)
            if not hundredthPlace:
                # Might be zero. Ignore.
                pass
            else:
                hundredsInWords = '%s hundred' % self.wordsDict[hundredthPlace]
                wordList.insert(0, hundredsInWords)

        # ---------------------------------------------------------------------#
        if MSBs:
            MSBs.reverse()

            for idx, item in enumerate(MSBs):
                inWords = self._formulateDoubleDigitWords(int(item))
                if inWords:
                    inWordsWithDenomination = '%s %s' % (inWords, self.powerNameList[idx])
                    wordList.insert(0, inWordsWithDenomination)

        # ---------------------------------------------------------------------#
        return wordList

    def _formulateDoubleDigitWords(self, doubleDigit):

        if not int(doubleDigit):
            # Might be zero. Ignore.
            return None
        elif int(doubleDigit) in self.wordsDict:
            # Global dict has the key for this number
            tensInWords = self.wordsDict[int(doubleDigit)]
            return tensInWords
        else:
            doubleDigitStr = str(doubleDigit)
            tens, units = int(doubleDigitStr[0]) * 10, int(doubleDigitStr[1])
            tensUnitsInWords = '%s %s' % (self.wordsDict[tens], self.wordsDict[units])
            return tensUnitsInWords


wGenerator = Number2Words()


def commafy(amount):
    if not amount:
        return
    amount_string = str(amount)
    after_point = ''
    if '.' in amount_string:
        amount_string, after_point = amount_string.split('.')
    last_three = amount_string[-3:]
    other_numbers = amount_string[:-3]
    if other_numbers:
        last_three = ',' + last_three
    return re.sub('\B(?=(\d{2})+(?!\d))', ',', other_numbers) + last_three + '.' + after_point
