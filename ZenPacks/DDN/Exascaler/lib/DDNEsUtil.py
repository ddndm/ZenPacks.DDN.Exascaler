import json
import logging

log = logging.getLogger('zen.zenesutil')


def EsParser(results, key, log):
    """
        Given the output of get_gs_metrics.py, look for the key and
        give out a dictionary
    """
    try:
        jsonres = json.loads(results)
    except Exception as e:
        log.error(
            'XXXX json load failed for %s Exception is %s' % (results, e))
        return {}
    if key:
        return jsonres.get(key)
    return jsonres


# New Api Implementation

def es_process_esmodel(results, key=''):
    results = EsParser(results, '', log)
    if key:
        return results.get(key)
    return results
