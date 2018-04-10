cdef datum_py2native(pd, datum& d):
    d.string_values_.clear()
    for k, v in pd.string_values:
        k = k.encode('utf8')
        v = v.encode('utf8')
        d.string_values_.push_back(pair[string, string](k, v))
    d.num_values_.clear()
    for k, v in pd.num_values:
        k = k.encode('utf8')
        d.num_values_.push_back(pair[string, double](k, v))
    d.binary_values_.clear()
    for k, v in pd.binary_values:
        k = k.encode('utf8')
        d.binary_values_.push_back(pair[string, string](k, v))

cdef datum_native2py(datum& d):
    ret = Datum()
    for i in range(d.string_values_.size()):
        k = d.string_values_[i].first.decode('utf8')
        v = d.string_values_[i].second.decode('utf8')
        ret.add_string(k, v)
    for i in range(d.num_values_.size()):
        k = d.num_values_[i].first.decode('utf8')
        v = d.num_values_[i].second
        ret.add_number(k, v)
    for i in range(d.binary_values_.size()):
        k = d.binary_values_[i].first.decode('utf8')
        v = d.binary_values_[i].second
        ret.add_binary(k, v)
    return ret

cdef props_py2native(p, prop_t& out):
    for k, v in p.items():
        out.insert(pair[string, string](k.encode('utf8'), v.encode('utf8')))

cdef props_native2py(prop_t& p):
    r = {}
    for it in p:
        r[it.first.decode('utf8')] = it.second.decode('utf8')
    return r

cdef edges_native2py(const vector[edge_id_t]& edges):
    ret = []
    for i in range(edges.size()):
        ret.append(edges[i])
    return ret

cdef preset_query_py2native(query, preset_query& q):
    for x in query.edge_query:
        q.edge_query.push_back(pair[string, string](
            x.from_id.encode('ascii'), x.to_id.encode('ascii')))
    for x in query.node_query:
        q.node_query.push_back(pair[string, string](
            x.from_id.encode('ascii'), x.to_id.encode('ascii')))

def check_ndarray_csr_type(X):
    import numpy as np
    cdef int is_ndarray = isinstance(X, np.ndarray)
    cdef int is_csr = (type(X).__name__ == 'csr_matrix')
    if not (is_ndarray or is_csr):
        raise ValueError
    if len(X.shape) != 2:
        raise ValueError('invalid X.shape')
    if X.dtype != np.float64:
        raise ValueError('X.dtype must be float64')
    if is_csr:
        if X.indices.dtype != np.int32:
            raise ValueError('X.indices.dtype must be int32')
        if X.indptr.dtype != np.int32:
            raise ValueError('X.indptr.dtype must be int32')
    return is_ndarray
