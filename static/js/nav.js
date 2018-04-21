/*导航当前页高亮*/

var As = document.getElementById('topnav').getElementsByTagName('a');
var obj = As[0];
for (i = 1; i < As.length; i++) {
    if (window.location.href.indexOf(As[i].href) >= 0){
        obj = As[i];
        break;
    }
}
obj.id = 'topnav_current'



