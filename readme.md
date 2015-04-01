
#leanote导出MD工具
- 可以把你储存在[Leanote](http://leanote.com)上的笔记、文章都导出成文本文件
- 导出格式参照 [hexo](http://hexo.io/docs/front-matter.html)  的文件格式，也就是说文件头部会有`title` `tags` `date` `categoris`等meta信息
- 兼容官方网站，以及自建的服务器（基于API 0.1版本）



#如何使用
- 首先安装Python2版本
- 请保证 `requests` `Pillow` 模块均已经安装。否则请用`pip install`来安装
- 然后在命令行执行`python LeanoteExportToMD.py`
  - 如果报错，应该是你的 python 路径问题，或者缺少某些python module
- 根据提示输入域名（默认是http://leanote.com）、用户邮箱、密码
  - 如果是自建服务器，请保证版本不低于 beta4
  - 域名不要忘记加`http://`
  - 记得用邮箱，而不是用户名


#功能

- [x] 读取、保存笔记本/子笔记本的note
- [x]  保存为兼容 hexo 的tag、category、date、title
- [x] 只保存不在垃圾箱的笔记
- [x] 数不尽的bug
- [ ] 根据是否为已发布的blog，生成post或者draft
- [x] 保存附件到本地
- [ ] 导入到leanote（如果有，也会是另一个项目）