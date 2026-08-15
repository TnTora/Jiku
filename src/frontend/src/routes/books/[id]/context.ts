import { createContext } from "svelte";

export interface EbookReaderOptions {
    font: string | undefined,
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

export const default_ebookreader_options: EbookReaderOptions = {
    font: undefined,
    font_size: 20,
    line_height: 2.25,
    vertical: true,
    paginated: true,
    show_progress_bar: true,
    show_progress_tokens: true,
    limit_progress_to_section: true,
}