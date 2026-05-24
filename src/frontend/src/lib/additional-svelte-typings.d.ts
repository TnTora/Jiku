declare module 'svelte/elements' {
	// add a new element
	export interface SvelteHTMLElements {
		'custom-button': HTMLButtonAttributes;
	}

	// add a new global attribute that is available on all html elements
	export interface HTMLAttributes<T> {
		onoutsideclick?: () => void;
	}

}

export {}; // ensure this is not an ambient module, else types will be overridden instead of augmented