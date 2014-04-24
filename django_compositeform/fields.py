class FormSetField(object):
    # Tracks each time a FormSetField instance is created. Used to retain
    # order.
    creation_counter = 0

    def __init__(self, formset_class):
        self.formset_class = formset_class

        # Increase the creation counter, and save our local copy.
        self.creation_counter = FormSetField.creation_counter
        FormSetField.creation_counter += 1

    def get_formset_prefix(self, form, name):
        '''
        Return the prefix that is used for the formset.
        '''

        return '{form_prefix}formset-{formset_name}'.format(
            form_prefix=form.prefix + '-' if form.prefix else '',
            formset_name=name)

    def get_formset_kwargs(self, form, name):
        '''
        Return the keyword arguments that are used to instantiate the formset.
        '''

        return {
            'prefix': self.get_formset_prefix(form, name)
        }

    def get_formset(self, form, name):
        '''
        Get an instance of the formset.
        '''

        formset = self.formset_class(
            form.data if form.is_bound else None,
            form.files if form.is_bound else None,
            **self.get_formset_kwargs(form, name))
        return formset

