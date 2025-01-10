import DateConverter from 'src/components/date/VikramSamvat.js'
import formatNumberWithCommas from '../formatNumberWithComma'
export default function useGenerateChequePdf(fields) {
  return `
    <div style="border: 2px solid black; padding: 20px;">
    <div style="text-align: right;">Date : ${fields.date}</div>
    <div style="text-align: right;">Miti : ${DateConverter.getRepresentation(
      fields.date,
      'bs'
    )}</div>
    <div style="margin-top: 20px; display: flex;"><span style="width: 40px; flex-grow: 0; flex-shrink: 0;">Pay:</span> <span style=" flex-grow: 1; border-bottom: 2px black dotted; padding-bottom:2px;">${
      fields.payee
    }</span></div>
    <div style="display: grid; grid-template-columns: 75% 25%; margin-top: 10px;">
        <div style="margin-top: 5px; display: flex;"><span style="width: 130px; flex-grow: 0; flex-shrink: 0;">Amount In Words:</span> <span style=" flex-grow: 1; border-bottom: 2px black dotted; padding-bottom:2px;">${
          fields.amount_in_words
        } only</span></div>
        <div style="margin-left: 20px; border: black 2px solid; padding: 3px 10px; text-align: right;">${
          formatNumberWithCommas(fields.amount)
        } -/</div>
    </div>
    <div style="margin-top: 15px;">Cheque number : &nbsp; # ${fields.cheque_no}</div>
    `
}
