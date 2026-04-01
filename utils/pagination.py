"""
自定义的分页组件，以后如果想要使用这个分页组件，你需要做如下几件事：

在视图函数中：
    def pretty_list(request):

        # 1.根据自己的情况去筛选自己的数据
        queryset = models.PrettyNum.objects.all()

        # 2.实例化分页对象
        page_obj = Pagination(request,queryset)

        context = {
            'search_data': search_data,
            'queryset': page_obj.page_queryset,  #分完页的数据
            'page_string': page_obj.html(), #页码
        }
        return render(request, 'pretty_list.html', context)

在HTML页面1中：
    {% for foo in queryset %}
        {{foo.xx}}
    {% endfor %}
    <ul class="pagination">
        {{ page_string }}
    </ul>
"""
from django.utils.safestring import mark_safe
from django.http.request import QueryDict
import copy

class Pagination(object):

    def __init__(self, request, queryset, page_size=10, page_params='page', plus=5):
        """
        :param request:请求的对象
        :param queryset:符合条件的数据，根据这个数据给他进行分页处理
        :param page_size:每页显示多少条数据
        :param page_params:在URL中传递的获取分页的可选参数：例如：/pretty/list/?page=21
        :param plus:显示当前页的 前或后几页（页码）
        """

        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict = query_dict

        self.page_params = page_params

        page = request.GET.get(page_params, "1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1
        self.page = page
        self.page_size = page_size

        self.start = (page - 1) * page_size
        self.end = page * page_size

        self.page_queryset = queryset[self.start:self.end]

        total_count = queryset.count()
        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1

        self.total_page_count = total_page_count
        self.plus = plus

    def html(self):
        # 计算出，显示当前页的前5页，后5页

        if self.total_page_count <= 2 * self.plus + 1:
            # 数据库中数据比较少，都没有达到11页
            start_page = 1
            end_page = self.total_page_count
        else:
            # 数据库中数据比较多 > 11页

            # 当前页<5时（小极值）
            if self.page <= self.plus:
                start_page = 1
                end_page = 2 * self.plus + 1
            else:
                # 当前页 > 5
                # 当前页+5 > 总页面
                if (self.page + self.plus) > self.total_page_count:
                    start_page = self.total_page_count - 2 * self.plus
                    end_page = self.total_page_count
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus

        # 页码
        page_str_list = []

        self.query_dict.setlist(self.page_params,[1])
        # print(self.query_dict.urlencode())

        # 首页
        page_str_list.append("<li><a href='?{}'>首页</a></li>".format(self.query_dict.urlencode()))

        # 上一页
        if self.page > 1:
            self.query_dict.setlist(self.page_params, [self.page - 1])
            prev = "<li><a href='?{}'><span aria-hidden='true'>«</span></a></li>".format(
                self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_params, [1])
            prev = "<li><a href='?{}'><span aria-hidden='true'>«</span></a></li>".format(self.query_dict.urlencode())
        page_str_list.append(prev)

        # 页面
        for i in range(start_page, end_page + 1):
            self.query_dict.setlist(self.page_params, [i])
            if i == self.page:
                ele = "<li class='active'><a href='?{}'>{}</a></li>".format(self.query_dict.urlencode(), i)
            else:
                ele = "<li><a href='?{}'>{}</a></li>".format(self.query_dict.urlencode(), i)
            page_str_list.append(ele)

        # 下一页
        if self.page < self.total_page_count:
            self.query_dict.setlist(self.page_params, [self.page + 1])
            last = "<li><a href='?{}'><span aria-hidden='true'>»</span></a></li>".format(self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_params, [self.total_page_count])
            last = "<li><a href='?{}'><span aria-hidden='true'>»</span></a></li>".format(
                self.query_dict.urlencode())
        page_str_list.append(last)

        # 尾页
        self.query_dict.setlist(self.page_params, [self.total_page_count])
        page_str_list.append("<li><a href='?{}'>尾页</a></li>".format(self.query_dict.urlencode()))

        # 跳转
        page_str_list.append(
            """
                <li>
                    <div style="float: left;width: 110px;margin-left:10px">
                        <form method="get">
                            <div class="input-group">
                                <input type="text" name="page" class="form-control" placeholder="页码">
                                <span class="input-group-btn">
                                    <button class="btn btn-default" type="submit">跳转</button>
                                </span>
                            </div>
                        </form>
                    </div>
                </li>
            """
        )
        #也可以在前端用{{page_string | safe}}这种管道符来做
        page_string = mark_safe(''.join(page_str_list))
        return page_string
