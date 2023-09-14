# Running Async Crawler on Flask and Pass to JS driven HTML

This is for collecting NVD search result and format in JIRA ticket.

## Tricks

### aiohttp (Python)

#### 1. Comprehension in `<class List>` + `For-loop`
```python
def foo(boo):
  return boo

foo_list = [ k for item in List1 for k in foo(item) ]

foo_list = [ foo(k) for item in List1 for k in item ]
```
#### 2. `pprint` is good

Print every thing pretty...

#### 3. aiohttp, async

Mostly, it needs a loop-object to use.

However, running `aiohttp` on Flask need `flask[async]`.

This might indicate already exists a loop object.

So that, I tried to call loop function like `run_until_complete()` bur in vain.

**Basic usage:**

1. `with aiohttp.ClientSession() as client` to create a Client Session will be cleaned up right after its job.
2. Create a list and append coroutine in to it. 
This will be like
```py
import aiohttp, asyncio


async def foo(boo, client):
  async with client.get(boo) as response:
    return await response
    

async with aiohttp.ClientSession() as client:
  list1 = [ '', '', '' ]
  task = [ foo(i, client) for item in list1]
  task = await asyncio.gather(*task)

# return will be stored into task
```


## Require

### Python

`flask[async]` and `aiohttp`

### HTML 
```HTML
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" integrity="sha384-4bw+/aepP/YC94hEpVNVgiZdgIC5+VKNBQNGCHeKRQN+PtmoHDEXuppvnDJzQIu9" crossorigin="anonymous">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" integrity="sha512-z3gLpd7yknf1YoNbCzqRKc4qyor8gaKU1qmn+CShxbuBusANI9QpRohGBreCFkKxLhei6S9CQXFEbbKuqLg0DA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
<link rel="stylesheet" href="https://unpkg.com/jquery-resizable-columns@0.2.3/dist/jquery.resizableColumns.css" >
<link rel="stylesheet" href="https://unpkg.com/bootstrap-table@1.22.1/dist/bootstrap-table.min.css">
<link rel="stylesheet" href="https://unpkg.com/bootstrap-table@1.22.1/dist/extensions/reorder-rows/bootstrap-table-reorder-rows.css">
<link rel="stylesheet" href="https://unpkg.com/bootstrap-table@1.22.1/dist/extensions/sticky-header/bootstrap-table-sticky-header.css">
<script src="https://cdn.jsdelivr.net/npm/jquery/dist/jquery.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/TableDnD/0.9.1/jquery.tablednd.js" integrity="sha256-d3rtug+Hg1GZPB7Y/yTcRixO/wlI78+2m08tosoRn7A=" crossorigin="anonymous"></script>
<script src="https://unpkg.com/jquery-resizable-columns@0.2.3/dist/jquery.resizableColumns.min.js"></script>
<script src="https://unpkg.com/bootstrap-table@1.22.1/dist/bootstrap-table.min.js"></script>
<script src="https://unpkg.com/bootstrap-table@1.22.1/dist/extensions/reorder-rows/bootstrap-table-reorder-rows.js"></script>
<script src="https://unpkg.com/bootstrap-table@1.22.1/dist/extensions/resizable/bootstrap-table-resizable.min.js"></script>
<script src="https://unpkg.com/bootstrap-table@1.22.1/dist/extensions/multiple-sort/bootstrap-table-multiple-sort.js"></script>
<script src="https://unpkg.com/bootstrap-table@1.22.1/dist/extensions/sticky-header/bootstrap-table-sticky-header.min.js"></script>
<script src="https://unpkg.com/clipboard@2/dist/clipboard.min.js"></script>
```
 
