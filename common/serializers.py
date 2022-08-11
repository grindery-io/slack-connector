
def serialize_channel(channel):
    return {
        "value": channel['id'],
        "label":  channel['name'],
        "sample":  channel['id']
    }
