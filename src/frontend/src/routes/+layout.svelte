<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { setJikuErrorsContext } from '$lib/utils/context';
	import { setConfirmationPopupContext } from '$lib/utils/context';
	import ErrorBox from '$lib/components/ErrorBox.svelte';
	import ConfirmationPopup from '$lib/components/ConfirmationPopup.svelte';
	import TextInputPopup from '$lib/components/TextInputPopup.svelte';
	import type { ConfirmationPopupContext } from '$lib/utils/context';


	let { children } = $props();
	// let test_errors = [{short: "test1", details:"test message 1"}, {short: "test2", details:"test message 2"}];
	let errors = $state([]);
	setJikuErrorsContext(errors);


	let confirmation_popup: ConfirmationPopupContext = $state({
		show_input_modal: false,
		use_modal_input: true,
		input_description: "",
		text_input_value: null,
		text_input_default: "",
		modalOk: () => { return; },
		modalCancel: () => { return; },
	});

	setConfirmationPopupContext(confirmation_popup);

	function resetInputModal() {
        confirmation_popup.show_input_modal = false;
        confirmation_popup.use_modal_input = true;
        confirmation_popup.input_description = "";
        confirmation_popup.text_input_value = null;
    }

	function modalOkWrapper() {
		let res = confirmation_popup.modalOk();
		Promise.resolve(res).then(
			resetInputModal
		);
	}

</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<ErrorBox {errors} />

{#if confirmation_popup.show_input_modal}
	{#if confirmation_popup.use_modal_input}
		<TextInputPopup 
			bind:text_input_value={confirmation_popup.text_input_value}
			text_input_default={confirmation_popup.text_input_default}
			text={confirmation_popup.input_description}
			onCancel={() => {
				confirmation_popup.modalCancel();
				resetInputModal();
			}}
			onOk={modalOkWrapper}
		/>
	{:else}
		<ConfirmationPopup
			text={confirmation_popup.input_description}
			onCancel={() => {
				confirmation_popup.modalCancel();
				resetInputModal();
			}}
			onOk={modalOkWrapper}
		/>
	{/if}
{/if}

{@render children()}
