import os
import json
import csv
from copy import deepcopy
import StringIO

from django.views.generic.base import TemplateView, View
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import FormView

from django import forms

STOPS_JSON = os.path.join(os.path.dirname(__file__), "stops.json")
with open(STOPS_JSON) as stopsfile:
    STOPS = json.load(stopsfile)

STOPS_BY_TRACK = {}
for stop in STOPS:
    if stop['id_percorso'] not in STOPS_BY_TRACK:
        STOPS_BY_TRACK[stop['id_percorso']] = []
    STOPS_BY_TRACK[stop['id_percorso']].append(stop)




class UploadFileForm(forms.Form):
    file  = forms.FileField()


    def clean(self):
        form_data = self.cleaned_data
        reader = csv.DictReader(form_data['file'], delimiter=";")
        percorsi = []
        try:
            for row in reader:
                percorsi.append(row['Percorso'])
        except:
            self._errors["file"] = self.error_class(["Errore file di input"])            
            del form_data['file']
            return form_data

        percorsi_set = list(set(percorsi))
        print percorsi_set
        
        if len(percorsi_set) is not 1:
            self._errors["file"] = self.error_class(["Errore file di input:percorsi diversi"])            
            del form_data['file']
            return form_data

        percorso = percorsi_set[0]
        if percorso not in STOPS_BY_TRACK:
            self._errors["file"] = self.error_class(["Errore file di input: percorso non trovato"])
            del form_data['file']
            return form_data



def get_stop_position(track_id, stop_id):
    #print track_id, stop_id
    
    for i, stop in enumerate(STOPS_BY_TRACK[track_id]):
        #print i, stop['id_fermata']
        if stop['id_fermata'] == stop_id:
            return i
    return None


def get_stop_by_position(track_id, stop_position):
    
    return STOPS_BY_TRACK[track_id][stop_position]
    



class CSVProcessView(FormView):
    template_name = "csv_process.html"
    form_class = UploadFileForm
    success_url = '/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        
        rfile = self.request.FILES['file']
        reader = csv.DictReader(rfile, delimiter=";")
        data = []
        for line in reader:
            data.append(line)

        percorso = data[0]['Percorso']

        data_shadow = []

        first_stop = data[0]['Fermata']
        first_stop_index = get_stop_position(percorso, first_stop)
        all_stops =  STOPS_BY_TRACK[percorso]
        added_stops = 0


        data_shadow.append(data[0])
        last_stops_added = 0;

        for x in range(first_stop_index+1, len(all_stops)):
            idx = x - first_stop_index
            item = get_stop_by_position(percorso, x)
            if len(data) > last_stops_added+1 and (item['id_fermata'] == data[last_stops_added+1]['Fermata']):
                data_shadow.append(data[last_stops_added+1])
                last_stops_added += 1
            else:
                copied = deepcopy(data[last_stops_added])
                for key in ['Stop', 'Start']:
                    del copied[key]
                copied['Fermata'] = item['id_fermata']
                data_shadow.append(copied)


        

        #print "!!!", len(data_shadow), len(STOPS_BY_TRACK[percorso]), added_stops
        
        output = StringIO.StringIO()
        writer = csv.DictWriter(output, fieldnames=reader.fieldnames, restval=reader.restval,
             #extrasaction='raise',
              dialect=reader.dialect, delimiter=";")
        
        writer.writeheader()
        for row in data_shadow:
            writer.writerow(row)


        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="OK_%s"' % rfile.name
        response.write(output.getvalue())
        return response

        #return super(CSVProcessView, self).form_valid(form)

        
