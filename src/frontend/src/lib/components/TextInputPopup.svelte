<script lang="ts">
    import ConfirmationPopup from "./ConfirmationPopup.svelte";
    import { onMount } from "svelte";

    let {text, onOk, onCancel, text_input_value = $bindable(null), text_input_default = ""} = $props()

    let input_el: HTMLInputElement;

    onMount(() => {
        input_el.focus();
        input_el.select();
    });

</script>

<ConfirmationPopup {text} {onOk} {onCancel}>
    <input
        bind:this={input_el}
        bind:value={text_input_value}
        type="text"
        defaultvalue={text_input_default}
        class="text-center bg-neutral-800 rounded-md"
        onkeydown={(event) => {
            switch (event.code) { 
                case "Enter":
                    onOk();
                    break;
                case "Escape":
                    onCancel();
                    break;
            }
        }}
    >
</ConfirmationPopup>