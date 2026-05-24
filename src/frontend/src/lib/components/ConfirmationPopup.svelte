<script lang="ts">
	import type { Snippet } from "svelte";
    import CenteredPopup from "./CenteredPopup.svelte";

    interface Props {
        text: string,
        onOk: () => void,
        onCancel: () => void,
        children?: Snippet,
    }

    let { text, onOk, onCancel, children }: Props = $props()

</script>

<CenteredPopup>
    <p>{text}</p>
    {@render children?.()}
    <div class="flex items-center justify-evenly gap-4">
        <button
            class="px-3 py-1 w-20 bg-neutral-800 rounded-full text-sm font-semibold hover:bg-neutral-700 active:bg-neutral-600"
            onclick={onOk}
        >
            Ok
        </button>
        <button
            class="px-3 py-1 w-20 bg-neutral-800 rounded-full text-sm font-semibold hover:bg-neutral-700 active:bg-neutral-600"
            onclick={onCancel}>
            Cancel
        </button>
    </div>
</CenteredPopup>