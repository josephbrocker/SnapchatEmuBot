import queue
import threading


class _DataSource:

    def __init__(self, file_name, delimiter=None):
        """ Threadsafe DataSource object that can update OG file.

        Set `.update()` to keep OG file updated with `.remove()`.
        """

        self.q1 = queue.Queue()
        self.q2 = queue.Queue()

        self.file_name = file_name
        self.delimiter = delimiter

        for line in self.load():
            self.q1.put(line)
        
        self.update_thread = None
    
    def update(self):
        """ Starts the thread that keeps OG file updated.
        """

        if self.update_thread:
            return

        self.update_thread = threading.Thread(target=self.thread, daemon=True)
        self.update_thread.start()

    def thread(self):
        """ Thread that removes entries in q2 from OG file.
        """

        endme = False

        while True:
            remove = []

            while True:
                try:
                    data = self.q2.get(block=not bool(remove))

                    if data == ":peepoStop:":
                        endme = True
                
                except queue.Empty:
                    break

                remove.append(data)
            
            old = self.load()

            new = list(set(old) - set(remove))

            with open(self.file_name, "w") as f:
                f.write("\n".join(new))
            
            if endme:
                break
    
    def load(self):
        """ Load all lines from file.
        """
        
        lines = []

        with open(self.file_name) as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue
                
                lines.append(line)
        
        return lines
    
    def get(self):
        """ Return parsed data from q1.
        """

        data = self.q1.get()

        if self.delimiter:
            data = data.split(self.delimiter)
        
        return data
    
    def put(self, data):
        """ Put parsed data back in q1.
        """

        if self.delimiter:
            data = self.delimiter.join(data)
        
        self.q1.put(data)
    
    def remove(self, data):
        """ Put parsed data in q2 so it can be removed from OG file.
        """

        if self.delimiter:
            data = self.delimiter.join(data)
        
        self.q2.put(data)
    
    def exit_thread(self):
        """ Tries to exit thread cleanly.
        """

        self.q2.put(":peepoStop:")

        self.update_thread.join()


# Create source for accounts
accounts = _DataSource("data/acc.txt", delimiter=":")

# Create source for usernames
usernames = _DataSource("data/usn.txt")
usernames.update()

# Create source for emails
emails = _DataSource("data/emails.txt", delimiter=":")
emails.update()