from django import forms
from .models import TblUsuario, TblCurriculo
from django.core.validators import RegexValidator

# ------------------ FORMULÁRIO DE USUÁRIO ------------------
class FrmUsuario(forms.ModelForm):
    txtTelefonePrincipal = forms.CharField(
        label='Telefone Principal',
        validators=[RegexValidator(r'^\d{10,11}$', message='Digite um telefone válido com DDD')]
    )

    txtTelefoneSecundario = forms.CharField(
        label='Telefone Secundário',
        required=False,
        validators=[RegexValidator(r'^\d{10,11}$', message='Digite um telefone válido com DDD')]
    )

    txtCEP = forms.CharField(
        label='CEP',
        validators=[RegexValidator(r'^\d{5}-?\d{3}$', message='Digite um CEP válido (00000-000)')]
    )

    class Meta:
        model = TblUsuario
        fields = '__all__'
        widgets = {
            'datNascimento': forms.DateInput(attrs={'type': 'date'})
        }


# ------------------ FORMULÁRIO DE CURRÍCULO ------------------
class FrmCurriculo(forms.ModelForm):
    decPretensaoSalarial = forms.DecimalField(
        label='Pretensão Salarial (R$)',
        max_digits=10, decimal_places=2,
        min_value=0
    )

    class Meta:
        model = TblCurriculo
        fields = '__all__'
        widgets = {
            'txtCurriculoPdf': forms.ClearableFileInput(),
            'txtCartaApresentacao': forms.ClearableFileInput(),
        }