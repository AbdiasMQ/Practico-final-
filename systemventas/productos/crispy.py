from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder# sirve para personalizar los formularios

class BaseFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'form-horizontal'
        self.label_class = 'col-md col-form-label' #clase de bootstrap para etiquetas
        self.field_class = 'col-md-9' #clase de bootstrap para campos
        self.render_required_fields = "True"