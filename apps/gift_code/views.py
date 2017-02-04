import openpyxl

from django.http import HttpResponse, Http404

from apps.gift_code.models import GiftCodeGen, GiftCodeRecord

def download_gift_code(request):
    gen_id = request.GET.get('gen_id', 0)
    try:
        gen_id = int(gen_id)
        gift_code_gen = GiftCodeGen.objects.get(id=gen_id)
    except:
        raise Http404()

    category = gift_code_gen.category.id
    ids = GiftCodeRecord.objects.filter(gen_id=gen_id).values_list('id', flat=True)

    wb = openpyxl.Workbook()
    ws = wb.worksheets[0]
    for _id in ids:
        ws.append([_id])

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename="{0}.xlsx"'.format(category.encode('utf-8'))
    wb.save(response)
    return response
