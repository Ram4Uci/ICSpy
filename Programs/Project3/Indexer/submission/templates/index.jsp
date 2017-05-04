<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">


<html>
<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>ICSpy</title>

</head>
<body>
<link rel="stylesheet" href="{{ url_for('static',filename='styles/myStyle.css') }}" />
<div class="center">
<h1 class="rainbow">ICSpy</h1>


	<form method="post" action="/query">
		<table>
			<tr>
				<td>Query</t>
				<input type="text" name="query"></td>
				
			</tr>
			
			<tr>
				<td><button type="submit" name="Search"> Search </button></td>				
			</tr>
		</table>	 
	</form>
</div>
	

</body>
</html>

