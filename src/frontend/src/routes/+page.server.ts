export const load = async ({ fetch }) => {
    let res = await fetch(`/api_bridge/options/anki_settings`);
	const anki_settings = await res.json();
    res = await fetch(`/api_bridge/books/books_info?ordr=2&asc=no&limit=10`);
    const books = await res.json();
    console.log(books);
    // console.log(anki_settings);
    res = await fetch("/api_bridge/anki/known_morphemes");
    const known_morphemes = await res.json();
	return { anki_settings, books, known_morphemes };
};