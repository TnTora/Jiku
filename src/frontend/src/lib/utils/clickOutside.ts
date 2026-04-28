export function clickOutside(node: Element) {
    const handleClick = (event: Event) => {
        if (!node.contains(event.target as Node)) {
            node.dispatchEvent(new CustomEvent("outsideclick"));
        }
    };

    document.addEventListener("click", handleClick, true);

    return {
        destroy() {
            document.removeEventListener("click", handleClick, true);
        },
    }
}