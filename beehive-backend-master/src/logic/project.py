def parse_links(ids, all_links):
            all_links_map = {l['task_id']: l for l in all_links}                   
            parsed = []
            for id in ids:
                day = id[0]
                links = []
                for i in id[1].split(','):
                     if i in all_links_map:
                         links.append(all_links_map[i])   
                p = (day, links)
                parsed.append(p)
            return parsed