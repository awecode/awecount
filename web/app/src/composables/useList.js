import useApi from './useApi'
import { withQuery } from 'ufo'
import { withTrailingSlash, joinURL } from 'ufo'
import DateConverter from '/src/components/date/VikramSamvat.js'
import { useLoginStore } from 'src/stores/login-info'
const store = useLoginStore()

const sortOnKeys = (dict) => {
  const sorted = []
  for (const key in dict) {
    sorted[sorted.length] = key
  }
  sorted.sort()
  const tempDict = {}
  for (let i = 0; i < sorted.length; i++) {
    tempDict[sorted[i]] = dict[sorted[i]]
  }

  return tempDict
}

const humanizeWord = (word) => {
  word = word.replace(/_/g, ' ')
  return word.charAt(0).toUpperCase() + word.slice(1)
}

export default (endpoint, predefinedColumns = null) => {
  const route = useRoute()
  const router = useRouter()
  const $q = useQuasar()

  const {
    page: pageQueryValue,
    q: qQueryValue,
    search: searchQueryValue,
    ...filterQueryValues
  } = route.query
  const pagination = ref({
    // sortBy: 'desc',
    // descending: false,
    page: 1,
    rowsPerPage: 4,
  })
  const aggregate = ref(null)
  const searchQuery = ref(searchQueryValue || qQueryValue || '')
  const loading = ref(false)
  const initiallyLoaded = ref(false)
  const page = ref(pageQueryValue || 1)
  const unCalculatedrows = ref([])
  // const rows = ref([])
  const columns = ref([])

  let cleanedFilterValues = Object.fromEntries(
    Object.entries(filterQueryValues).map(([k, v]) => {
      // debugger
      if (v === 'true') {
        return [k, true]
      } else if (v === 'false') {
        return [k, false]
      } else if (k === 'status' && typeof v === 'string') {
        // TODO: added as an temproary solution need to confirm with dipesh sir
        return [k, [`${v}`]]
      }
      return [k, v]
    })
  )
  // let cleanedFilterValues = Object.fromEntries(
  //   Object.entries(filterQueryValues).map(([k, v]) => {
  //     if (v === 'true') {
  //       return [k, true]
  //     } else if (v === 'false') {
  //       return [k, false]
  //     }
  //     return [k, v]
  //   })
  // )
  const filters = ref(cleanedFilterValues)

  function loadData() {
    loading.value = true
    let url = withQuery(endpoint, { page: page.value })
    if (searchQuery.value) {
      url = withQuery(url, { search: searchQuery.value })
    }
    if (filters.value) {
      url = withQuery(url, filters.value)
    }
    useApi(url)
      .then((response) => {
        unCalculatedrows.value = response.results
        initiallyLoaded.value = true
        pagination.value = {
          // sortBy: 'desc',
          // descending: false,
          page: response.pagination.page,
          rowsPerPage: response.pagination.size,
          rowsNumber: response.pagination.count,
        }

        if (predefinedColumns) {
          columns.value = predefinedColumns
        } else if (response.results?.length) {
          const fields = Object.keys(response.results[0]).filter(
            (f) => f !== 'id'
          )
          const columnList = fields.map((f) => {
            return {
              name: f,
              // required: true,
              label: humanizeWord(f),
              align: 'left',
              field: f,
              // format: (val) => `${val}`,
              // sortable: true,
            }
          })

          columnList.push({
            name: 'actions',
          })
          columns.value = columnList
        }
        // TODO: check With dipesh sir about removing this check
        // if (response.aggregate) {
        aggregate.value = response.aggregate || null
        // }
        // TODO: check With dipesh sir about removing this check
        loading.value = false
      })
      .catch((data) => {
        let message
        if (data.status == 404) {
          if (data.data?.detail) {
            message = `Not found - ${data.data.detail}`
          } else {
            message = 'Not found!'
          }
        }
        if (data.status == 403) {
          message = data.data.detail
          router.push('/NoPermission')
        }
        if (data.status == 500) {
          message = 'Server Error! Please contact us with the problem.'
        }
        $q.notify({
          color: 'red-6',
          message: message,
          icon: 'report_problem',
        })
        loading.value = false
      })
  }

  // loadData()
  // NOTE: removed because was making 2 calls

  function onRequest(props) {
    let url = route.fullPath
    if (props.pagination?.page == 1) {
      url = withQuery(url, { page: undefined })
    } else {
      url = withQuery(url, { page: props.pagination.page })
    }
    if (props.filter) {
      url = withQuery(url, { search: props.filter })
    } else {
      url = withQuery(url, { search: undefined })
    }
    router.push(url)
  }

  watch(
    () => route.query,
    (newQuery, oldQuery) => {
      const newPage = newQuery?.page || 1
      const oldPage = oldQuery?.page || 1
      if (newPage !== oldPage) {
        page.value = newPage
      }
      // if (newQuery?.search !== oldQuery?.search) {
      //   searchQuery.value = newQuery.search
      // }
      loadData()
    },
    { deep: true, immediate: true, flush: 'post' }
  )

  const onFilterUpdate = () => {
    let url = route.path
    // TODO: check with dipesh sir
    let totalFilters = { ...filters.value }
    totalFilters.search = searchQuery.value
    // TODO: check with dipesh sir
    let cleanedFilters = Object.fromEntries(
      Object.entries(totalFilters).map(([k, v]) => {
        if (v === null) {
          return [k, undefined]
        }
        return [k, v]
      })
    )
    // reset page
    cleanedFilters.page = undefined
    cleanedFilters = sortOnKeys(cleanedFilters)
    // TODO withQuery isn't preserving the order
    url = withQuery(url, cleanedFilters)
    url = url.replace('+', '%20')
    // debugger
    router.push(url)

    // url = withQuery(url, cleanedFilters)
    // // url = url.replace('+', '%20')
    // console.log(cleanedFilters)
    // router.push({ path: route.path, query: cleanedFilters })
  }
  const rows = computed(() => {
    if (
      unCalculatedrows.value.length > 0 &&
      !store.isCalendarInAD &&
      unCalculatedrows.value[0].hasOwnProperty('date')
    ) {
      let newData = []
      unCalculatedrows.value.forEach((item) => {
        const updatedItem = { ...item }
        if (updatedItem) {
          updatedItem.date = DateConverter.getRepresentation(item.date, 'bs')
        }
        newData.push(updatedItem)
      })
      return newData
    } else return unCalculatedrows.value
  })

  // watch(filters.value, () => {
  //   onFilterUpdate()
  // })

  const resetFilters = () => {
    filters.value = {}
    onFilterUpdate()
  }

  const confirmDeletion = (id) => {
    $q.dialog({
      title: '<span class="text-red">Delete?</span>',
      message: 'Are you sure you want to delete?',
      cancel: true,
      html: true,
    }).onOk(() => {
      const deleteEndpoint = withTrailingSlash(joinURL(endpoint, id + ''))
      useApi(deleteEndpoint, {
        method: 'DELETE',
      }).then(() => {
        // rows.value = rows.value.filter((r) => r.id != id)
        const pg = pagination.value
        const isLastPage = Math.ceil(pg.rowsNumber / pg.rowsPerPage) == pg.page
        // check if last page, has only 1 item and is not the first page
        if (
          isLastPage &&
          (pg.rowsPerPage === 1 || pg.rowsNumber % pg.rowsPerPage === 1) &&
          pg.page != 1
        ) {
          let url = route.fullPath
          url = withQuery(url, { page: page.value - 1 })
          router.push(url)
        } else {
          loadData()
        }
        $q.notify({
          color: 'positive',
          message: 'Deleted',
          icon: 'check_circle',
        })
      })
    })
  }

  return {
    columns,
    rows,
    resetFilters,
    onFilterUpdate,
    filters,
    loading,
    searchQuery,
    pagination,
    onRequest,
    confirmDeletion,
    initiallyLoaded,
    aggregate,
  }
}
