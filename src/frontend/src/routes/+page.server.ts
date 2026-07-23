import type { BookInfoResponse } from '$lib/api_types/books.js';
import type { AnkiInfoRespone, AnkiSettingsRespone, KnownMorphemes } from '$lib/api_types/core.js';
import type { PresetInfo } from '$lib/api_types/texthooker.js';

export const load = async ({ fetch }) => {
    let res = await fetch(`/api_bridge/options/anki_settings`);
	const anki_settings: AnkiSettingsRespone = await res.json();
    console.log(anki_settings);
    res = await fetch(`/api_bridge/books/books_info?ordr=2&asc=no&limit=10`);
    const books: BookInfoResponse[] = await res.json();
    console.log(books);
    res = await fetch("/api_bridge/anki/known_morphemes");
    const known_morphemes: KnownMorphemes = await res.json();
    res = await fetch("/api_bridge/anki/anki_decks_info");
    const anki_info: AnkiInfoRespone = await res.json();
    console.log(anki_info);
    res = await fetch("/api_bridge/texthooker/presets");
    const presets: string[] = await res.json();
    console.log(presets);
    res = await fetch("/api_bridge/texthooker/presets_info");
    const presets_info: PresetInfo[] = await res.json();
    console.log(presets_info);
	return { anki_settings, books, known_morphemes, anki_info, presets, presets_info };
};