import os
import shutil
import logging
import datetime
import markdown
import pyjello_conf as pjc
import re


def util_backup(filename):
    ts = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
    newname = filename + '.' + ts + '.bkp'
    try:
        shutil.copy2(filename, newname)
        logging.info('File %s backed up as %s.' % (filename, newname))
    except Exception as e:
        logging.error('Failed to backup file %s due to %s' % (filename, str(e)))
        pass
    return True

def util_build_file_list(dirname, IGNORE_CREGEX):
    """
       Builds a list of dictionaries of the form -
          * { 'dir': ..., 'filename': ..., 'ctime': ..., 'mtime': ... }
    """
    outlist = []
    logging.info('Scanning directory: %s', dirname)
    try:
        with os.scandir(dirname) as filelist:
            filelist_filt = [a for a in filelist if a.is_file() and not any(list(map(lambda rg: True if rg.match(a.name) else False, IGNORE_CREGEX)))]
            outlist = [ {'dir': dirname, 'filename': a.name, 'ctime': a.stat().st_ctime, 'mtime': a.stat().st_mtime} for a in filelist_filt ]
            dirlist = [ a for a in filelist if a.is_dir() ]
            if len(dirlist) > 0:
                outlist.append(list(map(util_build_file_list, dirlist)))
    except FileNotFoundError:
        logging.error('Directory not found: %s' % dirname)
        pass
    except Exception as e:
        logging.error('Error due to %s' % e) 
    logging.debug('Filelist generated for %s as %s' % (dirname, outlist))
    return outlist

def util_sqlite_dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def util_md_meta_cleanup(text):
    """
    The markdown extension code-fence clobbers md.lines (which is an internal var anyway).
    Due to this, using md.lines to rebuild the md file with appropriate default meta tags included did not 
    work.
    This function uses a subset of the regex from the python-markdown meta extension to remove meta tags
    and returns only the content
    """
    META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
    END_RE = re.compile(r'^((-{3}|\.{3})(\s.*)?)|\s*')
    out = []
    inmetablock = 1 # Assumption : Meta blocks are at the beginning.
    for line in text.split('\n'):
        if META_RE.match(line) and inmetablock==1:
            logging.debug('Tag line matched for %s. Continuing' % line)
            continue
        elif END_RE.match(line) and inmetablock==1:
            logging.debug('End tag matched for %s. Setting inmetablock to 0.' % line)
            inmetablock = 0
        elif inmetablock == 0:
            logging.debug('Good content. Appending. %s' % line)
            out.append(line)
        else:
            logging.error('Meta tag structure borked. You should not be here. %s' % line)
    return out
