@app.route("/accounts/filter/")
async def get_user(request):
    print(request.args)
    query = Account.query

    for arg, val in request.args.items():
        val = val[0]
        if arg == 'limit':
            query = query.limit(val)
        elif arg=='fname_eq':
            query = query.where(Account.fname==val)
        elif arg == 'sname_eq':
            query = query.where(Account.sname == val)

    query = query.order_by(Account.id.desc())
    accs = await query.gino.all()
    accs_json = []
    for a in accs:
        accs_json.append({
            'id': a.id,
            'email': a.email,
            'fname': a.fname,
            'sname': a.sname
        })
    return json({
        'accounts':accs_json
    })
