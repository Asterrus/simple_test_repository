def on_created(hashMap,_files=None,_data=None):
    from ru.travelfood.simple_ui import SimpleUtilites as suClass
    import json
    hashMap.put('CVDetectors', 'barcode')
    hashMap.put('CVSingleDetector', '')
    hashMap.put('CVSkipNested', '')
    hashMap.put('UseVisionSettings', '')
    settings = {
        "min_length": 2,
        "max_length": 6,
        "ReplaceO": False,
        "ToUpcase": False,
        "OnlyNumbers": True
    }
    hashMap.put("SetVisionSettings", json.dumps(settings))
    suClass.setGlobalHashMap('_object_detector_mode', '[]')
    return hashMap


def on_object_detected(hashMap,_files=None,_data=None):
    from ru.travelfood.simple_ui import SimpleUtilites as suClass
    import json
    current_object = hashMap.get('current_object')
    if not current_object:
        hashMap.put('toast', 'no_object')
    else:
        current_object = json.loads(current_object)
        print(current_object)
        obj_id = current_object['object_id']
        obj_value = current_object['value']

        odm = suClass.getGlobalHashMap('_object_detector_mode')
        print(odm, type(odm))
        odm = json.loads(odm) if odm else []
        if obj_value == '2762':
            for item in odm:
                item['mode'] = 'stop'
        else:
            odm.append({'object_id': obj_id, 'mode': "ocr"})
        suClass.setGlobalHashMap('_object_detector_mode', json.dumps(odm))
        print(suClass.getGlobalHashMap('_object_detector_mode'))
        hashMap.put('info', str(odm))


