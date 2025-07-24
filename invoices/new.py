from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
from .models import Invoice, Quote


def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})


def quote_list(request):
    quotes = Quote.objects.all()
    return render(request, 'invoices/quote_list.html', {'quotes': quotes})


def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice, 'request': request})


def quote_detail(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    return render(request, 'invoices/quote_detail.html', {'quote': quote, 'request': request})


def invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    html_string = render_to_string('invoices/invoice_pdf.html', {'invoice': invoice})

    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file)
    pdf_file.seek(0)

    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
    return response


def quote_pdf(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    html_string = render_to_string('invoices/quote_pdf.html', {'quote': quote})

    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file)
    pdf_file.seek(0)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quote_{quote.id}.pdf"'
    return response
