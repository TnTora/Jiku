<script lang="ts">
	import type { CollectionInfoResponse } from "$lib/api_types/books";
    import SelectionPopup from "$lib/components/SelectionPopup.svelte";

    interface Props {
        text: string,
        collections: CollectionInfoResponse[],
        select_value: number | null,
        onOk: () => void,
        onCancel: () => void,
    }

    let {text, onOk, onCancel, collections, select_value = $bindable(null)}: Props = $props()

    let options = collections.map((el) => {
        return {
            name: el.name, 
            value: el.id
        }
    });

    if (options.length == 0) {
        text = "No Collection found"
    }

</script>

<SelectionPopup bind:select_value={select_value} {text} {onOk} {onCancel} {options}/>