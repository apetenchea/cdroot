#include<iostream>
using namespace std;
char *c;
int F(int x)
{
    int R;
    char o;
    if(!x) {
        for(R=F(1),o=*c;o=='+'||o=='-';o=*c)
            ++c,R=o=='+'?R+F(1):R-F(1);
    } else if(x==1) {
        for(R=F(2),o=*c;o=='*'||o=='/';o=*c)
            ++c,R=o=='*'?R*F(2):R/F(2);
    } else if(*c=='(')
        ++c,R=F(0),++c;
    else
        for(R=0;isdigit(*c);c++)
            R=10*R+*c-'0';
    return R;
}
int main()
{
    c=new char[100002],cin>>c,cout<<F(0);
    return 0;
}
