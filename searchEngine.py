import math
import os
import glob

class VectorCompare:
    def magnitude(self, concordance):
        if type(concordance) != dict:
            raise ValueError('Supplied Argument should be of type dict')
        total = 0
        for word, count in concordance.items():
            total += count ** 2
        return math.sqrt(total)

    def relation(self, concordance1, concordance2):
        if type(concordance1) != dict:
            raise ValueError('Supplied Argument 1 should be of type dict')
        if type(concordance2) != dict:
            raise ValueError('Supplied Argument 2 should be of type dict')
        topvalue = 0
        for word, count in concordance1.items():
            if word in concordance2:
                topvalue += count * concordance2[word]
        mag_product = self.magnitude(concordance1) * self.magnitude(concordance2)
        if mag_product != 0:
            return topvalue / mag_product
        else:
            return 0

    def concordance(self, document):
        if type(document) != str:
            raise ValueError('Supplied Argument should be of type string')
        con = {}
        for word in document.split(' '):
            if word in con:
                con[word] = con[word] + 1
            else:
                con[word] = 1
        return con

def load_documents_from_folder(folder_path):
    """从文件夹读取所有txt文件"""
    documents = {}
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    
    if not txt_files:
        print(f"在 {folder_path} 中没有找到任何 .txt 文件")
        return {}
    
    for file_path in txt_files:
        # 获取文件名（不含扩展名）作为标题
        filename = os.path.basename(file_path)
        title = os.path.splitext(filename)[0]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_id = len(documents)
            documents[doc_id] = {
                'title': title,
                'content': content,
                'file_path': file_path
            }
            print(f"已加载: {title}")
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")
    
    return documents

def save_index(index, index_file='index.txt'):
    """简单保存索引到文件"""
    with open(index_file, 'w', encoding='utf-8') as f:
        for doc_id, concord in index.items():
            f.write(f"DOC_{doc_id}\n")
            for word, count in concord.items():
                f.write(f"{word}:{count}\n")
            f.write("---\n")
    print(f"索引已保存到 {index_file}")

def main():
    # 设置文档文件夹路径
    docs_folder = input("\n请输入文档文件夹路径: ").strip()
    
    # 如果文件夹不存在，创建示例文档
    if not os.path.exists(docs_folder):
        os.makedirs(docs_folder)
        print(f"创建示例文件夹: {docs_folder}")
        print("请把你的 .txt 文档放入这个文件夹，或使用下面的示例文档：")
        
        # 创建示例文档
        example_docs = {
            'example_1.txt': 'Python is a great programming language for beginners and experts alike',
            'example_2.txt': 'Search engines use vector space models to find relevant documents',
            'example_3.txt': 'Machine learning and artificial intelligence are changing the world'
        }
        
        for filename, content in example_docs.items():
            with open(os.path.join(docs_folder, filename), 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  创建示例: {filename}")
    
    # 加载文档
    print("\n正在加载文档...")
    documents = load_documents_from_folder(docs_folder)
    
    if not documents:
        print("没有找到任何文档，程序退出。")
        return
    
    print(f"\n共加载 {len(documents)} 个文档")
    
    # 构建索引
    print("正在构建索引...")
    v = VectorCompare()
    index = {}
    
    for doc_id, doc_info in documents.items():
        # 转为小写并按空格分词（保持原作者风格）
        content_lower = doc_info['content'].lower()
        index[doc_id] = v.concordance(content_lower)
    
    print("索引构建完成！\n")
    
    # 保存索引（可选）
    save_choice = input("是否保存索引到文件？(y/n): ").lower()
    if save_choice == 'y':
        save_index(index)
    
    # 交互搜索
    print("\n" + "="*50)
    print("简单搜索引擎已就绪 (输入 'exit' 退出)")
    print("="*50 + "\n")
    
    while True:
        searchterm = input('请输入搜索词: ').strip()
        
        if searchterm.lower() == 'exit':
            print("再见！")
            break
        
        if not searchterm:
            print("请输入搜索词\n")
            continue
        
        query_conc = v.concordance(searchterm.lower())
        matches = []
        
        for doc_id in index:
            score = v.relation(query_conc, index[doc_id])
            if score > 0:
                matches.append((score, doc_id, documents[doc_id]['title']))
        
        if not matches:
            print("未找到相关结果。\n")
            continue
        
        matches.sort(reverse=True)
        
        print(f"\n找到 {len(matches)} 个相关文档 (显示前10个):")
        print("-" * 60)
        for i, (score, doc_id, title) in enumerate(matches[:10], 1):
            # 显示文档片段
            content_preview = documents[doc_id]['content'][:100].replace('\n', ' ')
            print(f"{i:2d}. 相关度: {score:.4f}")
            print(f"    标题: {title}")
            print(f"    片段: {content_preview}...")
            print()
        
        # 询问是否查看完整内容
        if matches:
            view_choice = input("是否查看某个文档的完整内容？(输入编号或直接按回车继续): ").strip()
            if view_choice.isdigit():
                idx = int(view_choice) - 1
                if 0 <= idx < len(matches[:10]):
                    _, doc_id, _ = matches[idx]
                    print("\n" + "="*60)
                    print(f"完整内容 - {documents[doc_id]['title']}")
                    print("="*60)
                    print(documents[doc_id]['content'])
                    print("="*60 + "\n")
        
        print()

if __name__ == "__main__":
    main()
