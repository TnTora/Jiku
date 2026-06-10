<script lang="ts">

    let { known_morphemes } = $props()

</script>

<div class="flex items-center bg-sky-500 w-fit rounded-b-md">
    <button class="bg-sky-600 hover:bg-sky-700 active:bg-sky-800 cursor-pointer px-2 py-1 rounded-bl-md">
        Sync
    </button>
    <button class="mx-2 cursor-pointer">
        Lemmas: {known_morphemes.lemmas}
    </button>
    <span>|</span>
    <button class="mx-2 cursor-pointer">
        Inflections: {known_morphemes.inflections}
    </button>
</div>