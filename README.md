### Tytuł projektu
**"Aplikacja do Udostępniania Ekranu w Czasie Rzeczywistym"**

### Osoby realizujące
- Paweł Cichocki

### Nr grupy
Grupa 13c

### Semestr
Semestr letni

### Rok
2024

---

## Opis ogólny zagadnienia

Celem projektu jest stworzenie aplikacji umożliwiającej udostępnianie ekranu w czasie rzeczywistym, która będzie wykorzystywać nowoczesne technologie kompresji i przesyłania danych. Aplikacja pozwala użytkownikom na bezproblemowe dzielenie się obrazem z ekranu swojego urządzenia z innymi użytkownikami poprzez sieć internetową.

## Metody obliczeniowe i biblioteki wykorzystane w projekcie

W projekcie wykorzystano następujące metody i biblioteki:

- **Python 3.x**: Główny język programowania używany w projekcie.
- **OpenCL**: Technologia używana do akceleracji obliczeń na urządzeniach GPU.
- **pyopencl**: Biblioteka umożliwiająca interakcję z OpenCL w Pythonie.
- **socket**: Umożliwia tworzenie połączeń sieciowych między serwerem a klientem.
- **pickle**: Służy do serializacji i deserializacji obiektów Pythona.
- **threading**: Umożliwia wielowątkowość, co pozwala na równoległe wykonywanie różnych zadań w programie.
- **time**: Umożliwia zarządzanie czasem, np. wstrzymywanie wykonywania kodu na określony czas.
- **numpy**: Biblioteka do obliczeń numerycznych w Pythonie, używana do pracy z tablicami i matrycami.
- **cv2 (OpenCV)**: Biblioteka do przetwarzania obrazów i wideo.
- **imutils**: Ułatwia operacje na obrazach i wideo za pomocą OpenCV.
- **lz4.frame**: Biblioteka do kompresji i dekompresji danych.
- **pyautogui**: Umożliwia automatyzację interakcji z użytkownikiem, np. pobieranie pozycji kursora
- **dxcam (bettercam)**: Używana do przechwytywania obrazu z ekranu.
- **tkinter**: Biblioteka do tworzenia interfejsów graficznych w Pythonie.

## Elementarne schematy opisujące działanie projektu

### Przepływ informacji

```
User -> Shares Screen -> ClientHandler -> Processes Screen Data -> FrameReceiver -> Receives Frame Data -> FrameDisplay -> Displays Frame -> Remote User
```

### Diagramy UML

#### Diagram klas
![Diagram klas](https://github.com/plytki/screenshare/assets/53957038/fcf95d56-b66f-4408-a523-f32630b933cb)


## Przesyłanie i interpretowanie obrazu przez klienta

Przesyłanie i interpretowanie obrazu przez klienta polega na wysłaniu podstawowej klatki na początku, na której potem będą wykonywane operacje. Aby zoptymalizować przesył danych przez sieć, wysyłane są tylko zmiany, które zaszły w obrazie, porównując poprzednią klatkę z teraźniejszą. Wszystkie pola, które nie zmieniły się, są zerowane, a te, które się zmieniły, zawierają aktualne dane.

### Metoda do obliczania różnic w obrazie
```python
@classmethod
def calculate_diff(cls, old_image, new_image):
    """
    Calculate the difference between two images.

    Args:
        old_image (np.ndarray): The previous frame.
        new_image (np.ndarray): The current frame.

    Returns:
        np.ndarray: The difference image with alpha channel for changed pixels.
    """
    diff_image = np.zeros_like(old_image)
    differences = old_image != new_image  # Find differences between the old and new images
    diff_image[differences] = (0xFF000000 |
                               (new_image[differences] & 0x00FFFFFF))  # Mark differences with alpha channel
    old_image[:] = new_image  # Update the old image with the new image
    return diff_image
```
Powyższa metoda oblicza różnice między dwiema klatkami obrazu. Zwraca ona obraz różnicowy, w którym zmienione piksele są oznaczone kanałem alfa.

### Wysyłanie danych przez socket TCP
Przesyłanie danych odbywa się przez socket TCP w formacie BGRA. Wysyłanie odwraca bajty, więc odbierane dane będą w innym formacie (BGRA -> ARGB). Na kliencie dane są przetwarzane z wykorzystaniem GPU.

### Przetwarzanie klatek na kliencie z użyciem GPU
```python
def __init__(self, frame_width, frame_height):
    """
    Initializes the OpenCLHandler with the given frame width and frame height.

    Args:
        frame_width (int): The width of the frames to be processed.
        frame_height (int): The height of the frames to be processed.
    """
    self.frame_width = frame_width
    self.frame_height = frame_height

    # OpenCL setup
    platform = cl.get_platforms()[0]  # Select the first platform
    device = platform.get_devices()[0]  # Select the first device
    self.context = cl.Context([device])
    self.queue = cl.CommandQueue(self.context, device)

    # OpenCL kernel code for processing image differences
    kernel_code = """
    __kernel void AddDiffKernel(__global unsigned int *BackBuffer, __global unsigned int *DiffBuffer, 
                                unsigned int BufferWidth, unsigned int BufferHeight) {
        unsigned int LinearIndex = get_global_id(0);

        if(LinearIndex >= (BufferWidth * BufferHeight)) return;

        unsigned char Alpha = (DiffBuffer[LinearIndex] >> 24) & 0xFF;

        if(Alpha) {
            BackBuffer[LinearIndex] = DiffBuffer[LinearIndex];
        }
    }
    """
    self.program_add_diff = cl.Program(self.context, kernel_code).build()

    # OpenCL buffers initialization
    mf = cl.mem_flags
    self.back_buffer = np.zeros((frame_height * frame_width,), dtype=np.uint32)
    self.back_buffer_cl = cl.Buffer(self.context, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=self.back_buffer)
    self.diff_buffer_cl = cl.Buffer(self.context, mf.READ_ONLY, self.back_buffer.nbytes)

def process_frame(self, received_frame):
    """
    Process the received frame using OpenCL.

    Args:
        received_frame (np.ndarray): The frame to process.
    """
    # Copy the received frame to the OpenCL buffer
    cl.enqueue_copy(self.queue, self.diff_buffer_cl, received_frame).wait()

    # Set kernel arguments
    add_diff_kernel = self.program_add_diff.AddDiffKernel
    add_diff_kernel.set_arg(0, self.back_buffer_cl)
    add_diff_kernel.set_arg(1, self.diff_buffer_cl)
    add_diff_kernel.set_arg(2, np.uint32(self.frame_width))
    add_diff_kernel.set_arg(3, np.uint32(self.frame_height))

    # Execute the kernel
    cl.enqueue_nd_range_kernel(self.queue, add_diff_kernel, (self.frame_width * self.frame_height,), None)
    cl.enqueue_copy(self.queue, self.back_buffer, self.back_buffer_cl).wait()
```
Powyższa klasa `OpenCLHandler` inicjalizuje kontekst OpenCL i kolejkę komend. Przetwarza klatki obrazu, porównując je z użyciem jądra OpenCL, co pozwala na szybsze wykonywanie obliczeń dzięki wykorzystaniu GPU.

## Dodanie obrazów i ich opis

### Server Config
![Server Config](https://github.com/plytki/screenshare/assets/53957038/ac67262b-831c-469f-aa59-aefc586659f7)


To okno konfiguracyjne serwera pozwala na ustawienie następujących parametrów:
- **Host**: Adres hosta, tutaj ustawiony na "0.0.0.0", co oznacza, że serwer będzie nasłuchiwał na wszystkich interfejsach sieciowych.
- **Port**: Numer portu, tutaj ustawiony na 9998.
- **Frame Width**: Szerokość ramki obrazu w pikselach, tutaj ustawiona na 1920.
- **Frame Height**: Wysokość ramki obrazu w pikselach, tutaj ustawiona na 1080.

Te parametry definiują rozdzielczość obrazu, który będzie przesyłany z serwera do klienta.

### Client Config
![Client Config](https://github.com/plytki/screenshare/assets/53957038/1c9faeea-4d66-43df-8279-3c0d7e9e8d8f)


To okno konfiguracyjne klienta pozwala na ustawienie następujących parametrów:
- **Host**: Adres hosta serwera, tutaj ustawiony na "host1.plytki.cc".
- **Port**: Numer portu, tutaj ustawiony na 9998.
- **Display Width**: Szerokość wyświetlacza w pikselach, tutaj ustawiona na 1920.
- **Display Height**: Wysokość wyświetlacza w pikselach, tutaj ustawiona na 1080.

Parametry width i height w kliencie służą tylko do skalowania okna wyświetlania obrazu. Parametry te nie wpływają na rozdzielczość przesyłanych danych.

## Podsumowanie

Projekt zakończył się sukcesem, spełniając wszystkie założenia. System zarządzania klientami i ramkami danych działa poprawnie, a wykorzystanie OpenCL znacząco przyspieszyło przetwarzanie danych. Testy wykazały poprawność implementacji i stabilność działania.

## Bibliografia

- Documentation for Python: https://docs.python.org/3/
- PyOpenCL Documentation: https://documen.tician.de/pyopencl/
- OpenCL Documentation: https://www.khronos.org/opencl/

## Link do repozytorium Github

[https://github.com/plytki/screenshare](https://github.com/plytki/screenshare)
