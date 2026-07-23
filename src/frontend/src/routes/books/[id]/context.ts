import { createContext } from "svelte";

export interface EbookReaderOptions {
    // font?: string,
    font_size: number,
    line_height: number,
    vertical: boolean,
    paginated: boolean,
    show_progress_bar: boolean,
    show_progress_tokens: boolean,
    limit_progress_to_section: boolean,
    // override_ebook_css?: boolean,
}

export type EbookReaderOptionsBooleanKey = {
    [K in keyof EbookReaderOptions]: EbookReaderOptions[K] extends boolean? K: never
}[keyof EbookReaderOptions]

export const [getEbookReaderOptionsContext, setEbookReaderOptionsContext] = createContext<EbookReaderOptions>();