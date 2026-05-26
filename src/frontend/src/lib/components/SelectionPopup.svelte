<script lang="ts">
    import ConfirmationPopup from "./ConfirmationPopup.svelte";
    import { onMount } from "svelte";

    let {text, onOk, onCancel, options, select_value = $bindable(null)} = $props()
    let select_el: HTMLSelectElement;

    onMount(() => {
        select_el.focus();
    })


</script>

<ConfirmationPopup {text} {onOk} {onCancel}>
    <select
        bind:this={select_el}
        bind:value={select_value}
        // onchange={() => {select_value.value = select_el.value}}
        class="text-center bg-neutral-800 rounded-md w-full mx-1"
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
        {#each options as opt}
            <option value={opt.value}>{opt.name}</option>
        {/each}
    </select>
</ConfirmationPopup>