def jsonify_gino_model(rec):
    if type(rec) == list:
        return [jsonify_gino_model(r) for r in rec]

    if hasattr(rec,'__table__'):
        columns = rec.__table__.columns
        d = {}
        for c in columns:
            fld = str(c).split('.')[1]
            d[fld] = getattr(rec,fld)
    else:
        #rec is plain obj
        d = rec

    return d
