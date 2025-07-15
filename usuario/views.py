from django.shortcuts import render, redirect
from .forms import FrmUsuario, FrmCurriculo

def fncCadastrarCurriculo(request):
    if request.method == 'POST':
        frmUsuario = FrmUsuario(request.POST, request.FILES)  # PASSAR request.FILES
        frmCurriculo = FrmCurriculo(request.POST, request.FILES)  # PASSAR request.FILES

        if frmUsuario.is_valid() and frmCurriculo.is_valid():
            objUsuario = frmUsuario.save()
            objCurriculo = frmCurriculo.save(commit=False)
            objCurriculo.intIdUsuario = objUsuario
            objCurriculo.save()
            return redirect('pagina_sucesso')
    else:
        frmUsuario = FrmUsuario()
        frmCurriculo = FrmCurriculo()

    return render(request, 'tela_cadastro.html', {
        'frmUsuario': frmUsuario,
        'frmCurriculo': frmCurriculo,
    })