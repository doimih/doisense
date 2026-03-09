import { useCmsStaticPage } from "./useCmsStaticPage";

export function useLegalCmsPage(baseSlug: string) {
  return useCmsStaticPage(baseSlug, 'legal')
}
