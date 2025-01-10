type FileOrString = File | string

export async function uploadFiles(
  file: FileOrString | FileOrString[],
  folder?: string
): Promise<string | string[]> {
  const formData = new FormData()
  if (folder) {
    formData.append('folder', folder)
  }
  const isArray = Array.isArray(file)
  const fileUrls = []
  if (isArray) {
    if (!file.length) {
      return []
    }
    for (let i = 0; i < file.length; i++) {
      if (!(file[i] instanceof File)) {
        fileUrls.push(file[i] as string)
        continue
      }
      formData.append('files', file[i])
    }
  } else {
    if (!(file instanceof File)) {
      return file as string
    }
    formData.append('files', file)
  }
  const response = await useApi('upload-file/', {
    method: 'POST',
    body: formData,
  })
  return file instanceof File ? response[0] : [...fileUrls, ...response]
}
