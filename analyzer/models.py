from django.db import models


class Motherboard(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    # 新增主板特有字段（全部设为可选）
    chipset = models.CharField(max_length=100, verbose_name='主芯片组', blank=True, null=True)
    audio_chip = models.CharField(max_length=100, verbose_name='音频芯片', blank=True, null=True)
    memory_type = models.CharField(max_length=50, verbose_name='内存类型', blank=True, null=True)
    max_memory = models.CharField(max_length=50, verbose_name='最大内存容量', blank=True, null=True)
    form_factor = models.CharField(max_length=50, verbose_name='主板板型', blank=True, null=True)
    dimensions = models.CharField(max_length=100, verbose_name='外形尺寸', blank=True, null=True)
    power_connector = models.CharField(max_length=100, verbose_name='电源插口', blank=True, null=True)
    power_phase = models.CharField(max_length=50, verbose_name='供电模式', blank=True, null=True)

    class Meta:
        verbose_name = '主板'
        verbose_name_plural = '主板'
        db_table = 'motherboards'

    def __str__(self):
        return self.title



class CPU(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    # 新增字段
    suitable_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='适用类型')
    cpu_series = models.CharField(max_length=100, null=True, blank=True, verbose_name='CPU系列')
    cpu_frequency = models.CharField(max_length=100, null=True, blank=True, verbose_name='CPU主频')
    max_turbo_frequency = models.CharField(max_length=100, null=True, blank=True, verbose_name='最高睿频')
    l3_cache = models.CharField(max_length=100, null=True, blank=True, verbose_name='三级缓存')
    socket_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='插槽类型')
    core_count = models.CharField(max_length=100, null=True, blank=True, verbose_name='核心数量')
    thread_count = models.CharField(max_length=100, null=True, blank=True, verbose_name='线程数')
    manufacturing_tech = models.CharField(max_length=100, null=True, blank=True, verbose_name='制作工艺')
    tdp = models.CharField(max_length=100, null=True, blank=True, verbose_name='热设计功耗(TDP)')
    turbo_boost_frequency = models.CharField(max_length=100, null=True, blank=True, verbose_name='动态加速频率')
    package_size = models.CharField(max_length=100, null=True, blank=True, verbose_name='封装大小')

    class Meta:
        verbose_name = 'CPU'
        verbose_name_plural = 'CPU'
        db_table = 'cpus'

    def __str__(self):
        return self.title


from django.db import models


class GPU(models.Model):
    # 基础信息
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='参考价'
    )
    jd_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='京东价'
    )
    jd_link = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='京东链接'
    )
    product_image = models.URLField(
        max_length=500,
        default='https://example.com/default.jpg',
        verbose_name='产品图片'
    )
    product_parameters = models.TextField(
        null=True,
        blank=True,
        verbose_name='产品参数'
    )

    # 芯片信息
    chip_manufacturer = models.CharField(
        max_length=50,
        verbose_name='芯片厂商',
        blank=True,
        null=True
    )
    gpu_chip = models.CharField(
        max_length=100,
        verbose_name='显卡芯片',
        blank=True,
        null=True
    )
    chip_series = models.CharField(
        max_length=100,
        verbose_name='显示芯片系列',
        blank=True,
        null=True
    )
    process_tech = models.CharField(
        max_length=50,
        verbose_name='制作工艺',
        blank=True,
        null=True
    )
    core_code = models.CharField(
        max_length=100,
        verbose_name='核心代号',
        blank=True,
        null=True
    )

    # 核心规格
    core_clock = models.CharField(
        max_length=50,
        verbose_name='核心频率',
        blank=True,
        null=True
    )
    stream_processors = models.CharField(
        max_length=50,
        verbose_name='流处理单元',
        blank=True,
        null=True
    )
    cuda_cores = models.CharField(
        max_length=50,
        verbose_name='CUDA核心',
        blank=True,
        null=True
    )

    # 显存规格
    memory_type = models.CharField(
        max_length=50,
        verbose_name='显存类型',
        blank=True,
        null=True
    )
    memory_size = models.CharField(
        max_length=50,
        verbose_name='显存容量',
        blank=True,
        null=True
    )
    memory_bus = models.CharField(
        max_length=50,
        verbose_name='显存位宽',
        blank=True,
        null=True
    )
    memory_clock = models.CharField(
        max_length=50,
        verbose_name='显存频率',
        blank=True,
        null=True
    )
    memory_bandwidth = models.CharField(
        max_length=50,
        verbose_name='内存带宽',
        blank=True,
        null=True
    )

    # 显示输出
    max_resolution = models.CharField(
        max_length=100,
        verbose_name='最大分辨率',
        blank=True,
        null=True
    )
    interface_type = models.CharField(
        max_length=50,
        verbose_name='接口类型',
        blank=True,
        null=True
    )
    io_ports = models.CharField(
        max_length=200,
        verbose_name='I/O接口',
        blank=True,
        null=True
    )

    # 电源需求
    power_connectors = models.CharField(
        max_length=100,
        verbose_name='电源接口',
        blank=True,
        null=True
    )
    recommended_psu = models.CharField(
        max_length=50,
        verbose_name='建议电源',
        blank=True,
        null=True
    )

    # 物理特性
    gpu_type = models.CharField(
        max_length=50,
        verbose_name='显卡类型',
        blank=True,
        null=True
    )
    cooling = models.CharField(
        max_length=100,
        verbose_name='散热方式',
        blank=True,
        null=True
    )
    model_number = models.CharField(
        max_length=100,
        verbose_name='产品型号',
        blank=True,
        null=True
    )
    dimensions = models.CharField(
        max_length=100,
        verbose_name='产品尺寸',
        blank=True,
        null=True
    )
    design = models.CharField(
        max_length=100,
        verbose_name='显卡设计',
        blank=True,
        null=True
    )

    # 技术支持
    api_support = models.CharField(
        max_length=200,
        verbose_name='3D API',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = '显卡'
        verbose_name_plural = '显卡'
        db_table = 'gpus'

    def __str__(self):
        return self.title


from django.db import models


class RAM(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    # 内存特有字段
    suitable_type = models.CharField(max_length=100, verbose_name='适用类型', blank=True, null=True)
    capacity = models.CharField(max_length=50, verbose_name='内存容量', blank=True, null=True)
    memory_type = models.CharField(max_length=50, verbose_name='内存类型', blank=True, null=True)
    frequency = models.CharField(max_length=50, verbose_name='内存主频', blank=True, null=True)

    class Meta:
        verbose_name = '内存'
        verbose_name_plural = '内存'
        db_table = 'rams'

    def __str__(self):
        return self.title


from django.db import models


class SSD(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    # SSD 特有字段
    capacity = models.CharField(max_length=50, verbose_name='存储容量', blank=True, null=True)
    size = models.CharField(max_length=20, verbose_name='硬盘尺寸', blank=True, null=True)
    interface = models.CharField(max_length=50, verbose_name='接口类型', blank=True, null=True)
    cache = models.CharField(max_length=50, verbose_name='缓存', blank=True, null=True)
    read_speed = models.CharField(max_length=50, verbose_name='读取速度', blank=True, null=True)
    write_speed = models.CharField(max_length=50, verbose_name='写入速度', blank=True, null=True)
    seek_time = models.CharField(max_length=50, verbose_name='平均寻道时间', blank=True, null=True)
    mtbf = models.CharField(max_length=50, verbose_name='平均无故障时间', blank=True, null=True)

    class Meta:
        verbose_name = '固态硬盘'
        verbose_name_plural = '固态硬盘'
        db_table = 'ssds'

    def __str__(self):
        return self.title
class Cooler(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    class Meta:
        verbose_name = '散热器'
        verbose_name_plural = '散热器'
        db_table = 'coolers'

    def __str__(self):
        return self.title


class PowerSupply(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    # 电源特有字段
    psu_type = models.CharField(max_length=50, verbose_name='电源类型', blank=True, null=True)
    cable_type = models.CharField(max_length=50, verbose_name='出线类型', blank=True, null=True)
    rated_power = models.CharField(max_length=50, verbose_name='额定功率', blank=True, null=True)
    max_power = models.CharField(max_length=50, verbose_name='最大功率', blank=True, null=True)
    motherboard_connector = models.CharField(max_length=100, verbose_name='主板接口', blank=True, null=True)
    hdd_connector = models.CharField(max_length=100, verbose_name='硬盘接口', blank=True, null=True)
    pfc_type = models.CharField(max_length=50, verbose_name='PFC类型', blank=True, null=True)
    efficiency = models.CharField(max_length=50, verbose_name='转换效率', blank=True, null=True)

    class Meta:
        verbose_name = '电源'
        verbose_name_plural = '电源'
        db_table = 'power_supplies'

    def __str__(self):
        return self.title


class Chassis(models.Model):
    # 原有字段保持不变
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    # 新增字段
    chassis_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='机箱类型')
    chassis_structure = models.CharField(max_length=100, null=True, blank=True, verbose_name='机箱结构')
    compatible_motherboard = models.CharField(max_length=255, null=True, blank=True, verbose_name='适用主板')
    power_design = models.CharField(max_length=100, null=True, blank=True, verbose_name='电源设计')
    expansion_slots = models.CharField(max_length=100, null=True, blank=True, verbose_name='扩展插槽')
    front_interface = models.CharField(max_length=255, null=True, blank=True, verbose_name='前置接口')
    chassis_material = models.CharField(max_length=100, null=True, blank=True, verbose_name='机箱材质')
    panel_thickness = models.CharField(max_length=50, null=True, blank=True, verbose_name='板材厚度')

    class Meta:
        verbose_name = '机箱'
        verbose_name_plural = '机箱'
        db_table = 'chassis'

    def __str__(self):
        return self.title


from django.db import models

class PriceHistory(models.Model):
    component_type = models.CharField(max_length=50)
    component_id = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '价格历史'
        verbose_name_plural = '价格历史'
        db_table = 'price_history'

    def __str__(self):
        return f"{self.component_type} {self.component_id} - {self.price} at {self.date}"