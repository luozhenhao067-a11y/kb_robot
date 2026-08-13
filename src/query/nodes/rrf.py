from main_process.base import NodeBase
from tool.json_format import json_format
from tool.logger import logger

# 打分机制
class rrf(NodeBase):
    name = 'rrf'
    def process(self,state):
        embedding_chunks = state.get('embedding_chunks')
        hyde_embedding_chunks = state.get('hyde_embedding_chunks')
        if not embedding_chunks:
            logger.info('embedding_chunks is None')
            raise Exception('embedding_chunks is None')
        if not hyde_embedding_chunks:
            logger.info('hyde_embedding_chunks is None')
            raise Exception('hyde_embedding_chunks is None')


        weight_embedding = [
            (embedding_chunks,1),
            (hyde_embedding_chunks,1),
        ]

        K = 60
        the_final_dict = {}
        for chunks,weight in weight_embedding:
            # print(chunks,weight)
            for idx,chunk in enumerate(chunks,start=1):
                chunk_id = chunk.get('id')
                chunk_score = chunk.get('score') + (weight/(idx+K))
                if not chunk_id in the_final_dict:
                    chunk['score'] = chunk_score
                    the_final_dict[chunk_id] = chunk
                else:
                    the_final_dict[chunk_id]['score'] += chunk_score
        # print(json_format(the_final_dict))

        rrf_chunks = sorted(the_final_dict.values(), key=lambda x: x.get('score'), reverse=True)
        # print(json_format(rrf_chunks))
        return {
            'rrf_chunks':rrf_chunks
        }


if __name__ == '__main__':
    mock_state = {
        "embedding_chunks": [
            {
                "content": "## HAK 180 烫金机\n\n 产品安全手册（简体中文）\n\n感谢您购买 HAK 180 烫金机。\n\n在使用本设备之前，请先阅读本手册，包括所有预防措施。阅读本手册后，请妥善保管。\n\n有关使用本设备的更多信息，请参阅使用说明书，其可在兄弟 (中国)商业有限公司技术服务支持网站 http://www.95105369.com/Web/Manuals.aspx 上找到。建议您先通读使用说明书，再使用本设备。\n\n如需获得常见问题解答、故障排除和说明书，请访问\n\nhttp://www.95105369.com。\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。",
                "item_name": "HAK180烫金机",
                "id": 468273566107338086,
                "section_title": "## HAK 180 烫金机",
                "file_title": "hak180产品安全手册",
                "score": 0.8333861231803894,
                "source": "local"
            },
            {
                "content": "## HAK 180 烫金机\n\n •\t对于保养、调整或维修事宜，请联系 Brother 呼叫中心或您当地的Brother 经销商。\n\n•\t如果本设备工作不正常或发生任何错误，请关闭本设备，拔下所有电缆，然后联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t本文档中提供的信息可能会随时更改，恕不另行通知。\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。\n\n•\t请注意，对于使用通过本设备制作的产品造成的任何损坏或利润损失，或者故障、维修导致的数据消失或更改，或者第三方提出的任何索赔，我们不承担任何责任。",
                "item_name": "HAK180烫金机",
                "id": 468273566107338087,
                "section_title": "## HAK 180 烫金机",
                "file_title": "hak180产品安全手册",
                "score": 0.8302764892578125,
                "source": "local"
            },
            {
                "content": "## 设备\n\n •\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。\n\n•\t请勿尝试自行维修本设备。打开或拆下盖子可能使您接触到危险电压点以及带来其他风险，并且可能使您的保修失效。对于所有维修事宜，请联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t请在以下环境使用本设备：温度保持在 10 °C 和 32 °C 之间，湿度保持在 20% 和 80% 之间，无冷凝。\n\n•\t请勿使本设备受到阳光直射、过热、接触明火、腐蚀性气体、湿气或灰尘。否则可能产生触电、短路或火灾的风险，从而导致损坏设备和/或导致设备无法运行。\n\n•\t请勿将设备放在加热器、空调、电风扇或水附近。",
                "item_name": "HAK180烫金机",
                "id": 468273566107338090,
                "section_title": "## 设备",
                "file_title": "hak180产品安全手册",
                "score": 0.8252315521240234,
                "source": "local"
            },
            {
                "content": "## 设备\n\n ![图片警示：禁止将手伸入设备进纸/出纸区域，避免手指受伤；搬运设备时需双手抓稳机身底部，勿握托板或出纸盒以防掉落。](http://192.168.100.128:9000/knowledge-base/upload-images/5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg)",
                "item_name": "HAK180烫金机",
                "id": 468273566107338100,
                "section_title": "## 设备",
                "file_title": "hak180产品安全手册",
                "score": 0.8157632946968079,
                "source": "local"
            },
            {
                "content": "## 设备\n\n •\t请先阅读这本手册，再尝试操作本设备或尝试进行任何维护。不按照这些说明操作可能会提高发生人员受伤或财产损坏（包括火灾、触电、烧伤或窒息所致）的风险。对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t请勿在未去除所有包装材料的情况下使用本设备，包括本设备内部的任何附加的包装材料。否则可能会产生火灾的风险。\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。",
                "item_name": "HAK180烫金机",
                "id": 468273566107338089,
                "section_title": "## 设备",
                "file_title": "hak180产品安全手册",
                "score": 0.8157312870025635,
                "source": "local"
            },
            {
                "content": "## 设备\n\n如果遵守了操作说明进行操作，但是设备不能正确运行，请仅调整操作说明中涵盖的控制。错误调整其他控制可能导致损坏并且通常需要合格技术进行全面工作以将本设备恢复到正常操作。Brother不建议使用 Brother 正品烫金膜盒以外的其他品牌烫金膜盒。如果使用与本设备不兼容的耗材导致损坏本设备的任何零件，由此导致的任何维修可能不在保修范围内。\n",
                "item_name": "HAK180烫金机",
                "id": 468273566107338106,
                "section_title": "## 设备",
                "file_title": "hak180产品安全手册",
                "score": 0.8109999299049377,
                "source": "local"
            },
            {
                "content": "![图片展示的是HAK 180烫金机的产品安全手册封面，包含条形码、产品型号D01WD7001-00、品牌SCHN及兄弟（中国）技术支持网址，提示用户使用前需阅读手册并妥善保管。](http://192.168.100.128:9000/knowledge-base/upload-images/677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg)  \nD01WD7001-00\n\nSCHN\n",
                "item_name": "HAK180烫金机",
                "id": 468273566107338085,
                "section_title": "无题",
                "file_title": "hak180产品安全手册",
                "score": 0.8074419498443604,
                "source": "local"
            },
            {
                "content": "## 设备\n\n •\t将本设备放置在平整、水平且稳定的表面上（如桌面），避免震动和冲击。\n\n•\t将本设备放置在通风良好的环境中。\n\n•\t为了防止人员受伤，请谨慎操作，避免将手指放置在图中所示的区域中。\n\n![图片警示：严禁将手指伸入设备内部齿轮或传动机构区域，以防夹伤；强调操作时需避免手部接触危险部位，确保人身安全。](http://192.168.100.128:9000/knowledge-base/upload-images/c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg)",
                "item_name": "HAK180烫金机",
                "id": 468273566107338099,
                "section_title": "## 设备",
                "file_title": "hak180产品安全手册",
                "score": 0.7078579068183899,
                "source": "local"
            },
            {
                "content": "## 为设备选择一个安全的位置\n\n ![图片示意正确与错误的设备搬运方式：错误方式是单手提拉进纸托板或出纸盒，易致部件脱落；正确方式是双手稳握设备两侧底部，确保安全稳固搬运。](http://192.168.100.128:9000/knowledge-base/upload-images/cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg)",
                "item_name": "HAK180烫金机",
                "id": 468273566107338103,
                "section_title": "## 为设备选择一个安全的位置",
                "file_title": "hak180产品安全手册",
                "score": 0.6919587254524231,
                "source": "local"
            },
            {
                "content": "## 为设备选择一个安全的位置\n\n ![图示禁止将设备放置在桌边或支架边缘，尤其避免出纸盒打开时悬空；应确保设备完全置于平整、稳定、水平的表面，防止跌落造成人身伤害或设备损坏。](http://192.168.100.128:9000/knowledge-base/upload-images/8e839864036a7326885565163d99117ea943ecd29a656c85e7aa4052a9b9d28d.jpg)\n\n“重要事项”表示可能导致财产损失或本设备功能丧失的潜在危险情况。",
                "item_name": "HAK180烫金机",
                "id": 468273566107338105,
                "section_title": "## 为设备选择一个安全的位置",
                "file_title": "hak180产品安全手册",
                "score": 0.6913944482803345,
                "source": "local"
            }
        ],
        "hyde_embedding_chunks": [
            {
                "item_name": "HAK180烫金机",
                "section_title": "## HAK 180 烫金机",
                "id": 468273566107338086,
                "file_title": "hak180产品安全手册",
                "content": "## HAK 180 烫金机\n\n 产品安全手册（简体中文）\n\n感谢您购买 HAK 180 烫金机。\n\n在使用本设备之前，请先阅读本手册，包括所有预防措施。阅读本手册后，请妥善保管。\n\n有关使用本设备的更多信息，请参阅使用说明书，其可在兄弟 (中国)商业有限公司技术服务支持网站 http://www.95105369.com/Web/Manuals.aspx 上找到。建议您先通读使用说明书，再使用本设备。\n\n如需获得常见问题解答、故障排除和说明书，请访问\n\nhttp://www.95105369.com。\n\n对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。",
                "score": 0.8546012043952942,
                "source": "local"
            },
            {
                "item_name": "HAK180烫金机",
                "section_title": "## HAK 180 烫金机",
                "id": 468273566107338087,
                "file_title": "hak180产品安全手册",
                "content": "## HAK 180 烫金机\n\n •\t对于保养、调整或维修事宜，请联系 Brother 呼叫中心或您当地的Brother 经销商。\n\n•\t如果本设备工作不正常或发生任何错误，请关闭本设备，拔下所有电缆，然后联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t本文档中提供的信息可能会随时更改，恕不另行通知。\n\n•\t严禁未经授权擅自复制或重制本文档的任何部分或全部内容。\n\n•\t请注意，对于使用通过本设备制作的产品造成的任何损坏或利润损失，或者故障、维修导致的数据消失或更改，或者第三方提出的任何索赔，我们不承担任何责任。",
                "score": 0.8474220037460327,
                "source": "local"
            },
            {
                "item_name": "HAK180烫金机",
                "section_title": "## 设备",
                "id": 468273566107338090,
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n •\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。\n\n•\t请勿尝试自行维修本设备。打开或拆下盖子可能使您接触到危险电压点以及带来其他风险，并且可能使您的保修失效。对于所有维修事宜，请联系 Brother 呼叫中心或您当地的 Brother 经销商。\n\n•\t请在以下环境使用本设备：温度保持在 10 °C 和 32 °C 之间，湿度保持在 20% 和 80% 之间，无冷凝。\n\n•\t请勿使本设备受到阳光直射、过热、接触明火、腐蚀性气体、湿气或灰尘。否则可能产生触电、短路或火灾的风险，从而导致损坏设备和/或导致设备无法运行。\n\n•\t请勿将设备放在加热器、空调、电风扇或水附近。",
                "score": 0.8417571187019348,
                "source": "local"
            },
            {
                "item_name": "HAK180烫金机",
                "section_title": "## 设备",
                "id": 468273566107338106,
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n如果遵守了操作说明进行操作，但是设备不能正确运行，请仅调整操作说明中涵盖的控制。错误调整其他控制可能导致损坏并且通常需要合格技术进行全面工作以将本设备恢复到正常操作。Brother不建议使用 Brother 正品烫金膜盒以外的其他品牌烫金膜盒。如果使用与本设备不兼容的耗材导致损坏本设备的任何零件，由此导致的任何维修可能不在保修范围内。\n",
                "score": 0.8379123210906982,
                "source": "local"
            },
            {
                "item_name": "HAK180烫金机",
                "section_title": "## 设备",
                "id": 468273566107338089,
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n •\t请先阅读这本手册，再尝试操作本设备或尝试进行任何维护。不按照这些说明操作可能会提高发生人员受伤或财产损坏（包括火灾、触电、烧伤或窒息所致）的风险。对于本设备所有者不遵守本指南中规定的说明操作而导致的损害，Brother 不承担任何责任。\n\n•\t请勿在未去除所有包装材料的情况下使用本设备，包括本设备内部的任何附加的包装材料。否则可能会产生火灾的风险。\n\n•\t请勿拆解本设备。拆解本设备可能会导致火灾或触电。",
                "score": 0.8300846815109253,
                "source": "local"
            },
            {
                "item_name": "HAK180烫金机",
                "section_title": "## 设备",
                "id": 468273566107338100,
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n ![图片警示：禁止将手伸入设备进纸/出纸区域，避免手指受伤；搬运设备时需双手抓稳机身底部，勿握托板或出纸盒以防掉落。](http://192.168.100.128:9000/knowledge-base/upload-images/5067b2891ca4f761e2874921e0eb433aa742afbf38ca8dc509afecbf0aa6a6b5.jpg)",
                "score": 0.718265175819397,
                "source": "local"
            },
            {
                "item_name": "HAK180烫金机",
                "section_title": "## 设备",
                "id": 468273566107338099,
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n •\t将本设备放置在平整、水平且稳定的表面上（如桌面），避免震动和冲击。\n\n•\t将本设备放置在通风良好的环境中。\n\n•\t为了防止人员受伤，请谨慎操作，避免将手指放置在图中所示的区域中。\n\n![图片警示：严禁将手指伸入设备内部齿轮或传动机构区域，以防夹伤；强调操作时需避免手部接触危险部位，确保人身安全。](http://192.168.100.128:9000/knowledge-base/upload-images/c61a7f4e923881679f747508ae309c39dc221685344b068009256b1b3a40cc00.jpg)",
                "score": 0.7180286645889282,
                "source": "local"
            },
            {
                "item_name": "HAK180烫金机",
                "section_title": "## 设备",
                "id": 468273566107338094,
                "file_title": "hak180产品安全手册",
                "content": "## 设备\n\n ![图片警示：勿触摸设备内部高温区域（170°C/338°F），避免烫伤；禁止在设备运行时强行打开前盖；注意塑料袋窒息风险及起搏器用户远离弱磁场区域。](http://192.168.100.128:9000/knowledge-base/upload-images/f3349cded08d6686a93d0a81b9a64ec1e50d9a82cbb88541b37027f085813a15.jpg)  \n儎⑟ഴḽ䆜઀ᛞ࠽व䀜᪮儎⑟Ⲻ䇴༽䜞ԬȾ",
                "score": 0.7111523747444153,
                "source": "local"
            },
            {
                "item_name": "HAK180烫金机",
                "section_title": "无题",
                "id": 468273566107338085,
                "file_title": "hak180产品安全手册",
                "content": "![图片展示的是HAK 180烫金机的产品安全手册封面，包含条形码、产品型号D01WD7001-00、品牌SCHN及兄弟（中国）技术支持网址，提示用户使用前需阅读手册并妥善保管。](http://192.168.100.128:9000/knowledge-base/upload-images/677a08ee041965bbbdb6b483d6c17d5aaa36a26b6dc96870a2019f0307b8616f.jpg)  \nD01WD7001-00\n\nSCHN\n",
                "score": 0.7063151597976685,
                "source": "local"
            },
            {
                "item_name": "HAK180烫金机",
                "section_title": "## 为设备选择一个安全的位置",
                "id": 468273566107338103,
                "file_title": "hak180产品安全手册",
                "content": "## 为设备选择一个安全的位置\n\n ![图片示意正确与错误的设备搬运方式：错误方式是单手提拉进纸托板或出纸盒，易致部件脱落；正确方式是双手稳握设备两侧底部，确保安全稳固搬运。](http://192.168.100.128:9000/knowledge-base/upload-images/cc5ee1ac24ebb2707d40dc7a234a8b243f55f5bf08fabc683859be6fdf096ffa.jpg)",
                "score": 0.7047630548477173,
                "source": "local"
            }
        ]
    }
    node = rrf()
    res = node(mock_state)
    print(json_format(res))