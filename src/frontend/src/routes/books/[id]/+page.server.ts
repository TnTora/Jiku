export const load = async () => {
    const res = await fetch("http://127.0.0.1:8000/books/1");
	const book = await res.json();
    console.log(book);
	return {book};
};