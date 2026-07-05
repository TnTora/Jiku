export const load = async ({ fetch }) => {
    let res = await fetch(`/api_bridge/options/anki_settings`);
	const anki_settings = await res.json();
    res = await fetch(`/api_bridge/books/books_info?ordr=2&asc=no&limit=10`);
    const books = await res.json();
    console.log(books);
    // console.log(anki_settings);
    res = await fetch("/api_bridge/anki/known_morphemes");
    const known_morphemes = await res.json();
    res = await fetch("/api_bridge/anki/anki_decks_info");
    const anki_info = await res.json();
    console.log(anki_info);
	return { anki_settings, books, known_morphemes, anki_info };
};