/* eslint-disable regexp/no-unused-capturing-group */

const abbreviations = /^(pdf|url|api|http)$/i
const titleCaseExceptions = /^(a|an|and|as|at|but|by|for|if|in|is|nor|of|on|or|the|to|with)$/i

export const titelize = (str: string) => {
  return str
    .split(/[\s_-]/) // Split on space, underscore, or hyphen
    .map((word) => {
      if (abbreviations.test(word)) {
        return word.toUpperCase()
      }
      if (titleCaseExceptions.test(word)) {
        return word.toLowerCase()
      }
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    })
    .join(' ')
}
