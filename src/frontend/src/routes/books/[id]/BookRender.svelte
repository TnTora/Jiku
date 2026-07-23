<script lang="ts">
    import { tick } from "svelte";

    interface Props {
        content: string,
        onUpdateCallback: () => void
    }

    let { content , onUpdateCallback}: Props = $props();

    $effect.pre(() => {
        if (!content) { return };
        tick().then(() => {
            onUpdateCallback();
        });
    });

</script>

{@html content}

