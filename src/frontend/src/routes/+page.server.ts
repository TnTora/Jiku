export const load = async () => {
    let res = await fetch(`http://127.0.0.1:8000/options/anki_settings`);
	const anki_settings = await res.json();
    res = await fetch(`http://127.0.0.1:8000/books/books_info?ordr=2&limit=10`);
    const books = await res.json();
    console.log(anki_settings);
    res = await fetch("http://127.0.0.1:8000/anki/known_morphemes");
    const known_morphemes = await res.json();
	return { anki_settings, books, known_morphemes };
};