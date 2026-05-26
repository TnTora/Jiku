<script lang="ts">
    import SelectionPopup from "$lib/components/SelectionPopup.svelte";

    let {text, onOk, onCancel, collections, select_value = $bindable(null)} = $props()

    // svelte-ignore non_reactive_update
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