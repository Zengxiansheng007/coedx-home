import org.apache.jmeter.protocol.http.sampler.HTTPSampleResult

def origin = { URI uri ->
    [uri.scheme?.toLowerCase(Locale.ROOT), uri.host?.toLowerCase(Locale.ROOT),
     uri.port >= 0 ? uri.port : (uri.scheme.equalsIgnoreCase('https') ? 443 : 80)]
}
def current = new HTTPSampleResult(prev)
def uri = current.URL.toURI()
def allowedOrigin = origin(uri)
def method = sampler.method
def redirects = []
try {
    while (current.responseCode in ['301', '302', '303', '307', '308']) {
        redirects.add(current.responseCode)
        if (redirects.size() > 20) { throw new IllegalArgumentException('limit') }
        String location = current.redirectLocation
        if (!location) { throw new IllegalArgumentException('location') }
        URI next = uri.resolve(location)
        if (!next.host || next.rawUserInfo != null || origin(next) != allowedOrigin) {
            throw new IllegalArgumentException('origin')
        }
        if ((current.responseCode in ['301','302'] && method == 'POST') ||
            (current.responseCode == '303' && method != 'HEAD')) { method = 'GET' }
        def hop = sampler.clone()
        // Reuse the actual outbound session on this validated same-origin hop.
        def sessionHeader = current.cookies ?: (current.requestHeaders ?: '').readLines()
                .find { it.split(':', 2)[0].equalsIgnoreCase('Cookie') }?.split(':', 2)?.last()?.trim()
        if (sessionHeader) {
            hop.removeProperty('HTTPSampler.cookie_manager')
            def headers = hop.headerManager ?: new org.apache.jmeter.protocol.http.control.HeaderManager()
            headers.removeHeaderNamed('Cookie')
            headers.add(new org.apache.jmeter.protocol.http.control.Header('Cookie', sessionHeader))
            hop.removeProperty('HTTPSampler.header_manager')
            hop.setHeaderManager(headers)
        }
        hop.method = method
        if (method in ['GET','HEAD']) { hop.arguments.removeAllArguments(); hop.postBodyRaw = false }
        hop.path = (next.rawPath ?: '/') + (next.rawQuery != null ? '?' + next.rawQuery : '')
        current = hop.sample()
        prev.addSubResult(current)
        uri = next
        prev.responseCode = current.responseCode
        prev.responseMessage = current.responseMessage
        prev.responseData = current.responseData
        prev.contentType = current.contentType
        prev.dataEncoding = current.dataEncodingNoDefault
        prev.successful = current.successful
    }
} catch (Exception ignored) {
    prev.responseCode = 'REDIRECT_BLOCKED'
    prev.responseMessage = 'Redirect origin, location or hop limit rejected'
    prev.responseData = new byte[0]
    prev.successful = false
}
vars.put('redirect_codes', redirects.join('|'))
