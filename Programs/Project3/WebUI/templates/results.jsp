<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>{{title}}</title>
</head>

<body>
<h6>The Search Query results are</h6>
<h4>
{% for item in request.args.get('url_list','').split(',')%}
	{{item}}
		{% endfor %}}

</h4>



</body>
</html>