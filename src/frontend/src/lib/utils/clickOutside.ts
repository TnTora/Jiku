export function clickOutside(node: Element, exclude_query: string | null = null) {
    let excluded;
    if (exclude_query) {
        excluded = document.querySelectorAll(exclude_query);
    } else {
        excluded = [];
    }
        

    const handleClick = (event: Event) => {
        if (node.contains(event.target as Node)) {
            return;
        }

        for (const ex_node of excluded) {
            if (ex_node.contains(event.target as Node)) {
                return;
            }
        }
        
        node.dispatchEvent(new CustomEvent("outsideclick"));
    };

    document.addEventListener("click", handleClick, true);

    return {
        destroy() {
            document.removeEventListener("click", handleClick, true);
        },
    }
}