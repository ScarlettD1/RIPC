using System.Windows;
using System.Net.Http;
using Saraff.Twain;
using System.ComponentModel;
using System.Drawing.Imaging;
using System.Threading.Tasks;
using System.IO;
using iTextSharp.text;
using iTextSharp.text.pdf;
using System.Net.Http.Headers;

namespace RIPC_Scanner
{
    /// <summary>
    /// Логика взаимодействия для MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private string[] parametrs = ((App)Application.Current).Parameters;
        private static readonly HttpClient client = new HttpClient();
        private Twain32 twain;
        private string baseURL = "http://127.0.0.1:8000/api/scanned_page/scan";

        public MainWindow()
        {
            InitializeComponent();

            // Установка токена для запросов в сервис
            client.DefaultRequestHeaders.Add("token", "05fc8a08-b24a-4bbf-a1b2-82b645f26e28");

            // Установка переданных параметров
            SetParametrs();
            
            // Установка настроек Twain
            SetupTwain();

            // Обновление списка доступных сканеров
            GetDevices();
        }

        private void updateSButton_Click(object sender, RoutedEventArgs e)
        {
            // Обновление списка доступных сканеров
            GetDevices();
        }


        private void startScanButton_Click(object sender, RoutedEventArgs e)
        {
            // Подключение к сканеру
            try
            {
                twain.SourceIndex = sComboBox.SelectedIndex;
                if (!twain.OpenDataSource())
                {
                    MessageBox.Show("Не удалось открыть источник", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error);
                    return;
                }
            }
            catch 
            {
                MessageBox.Show("Сканер занят или недоступен.\n" +
                    "При многократной ошибке, попробуйте перезапустить компьютер и сканер.", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            // Установка необходимых параметров для сканирования
            try
            {
                twain.SetCap(TwCap.XResolution, (float)300);
                twain.SetCap(TwCap.YResolution, (float)300);
                twain.SetCap(TwCap.IPixelType, TwPixelType.RGB);
            }
            catch
            {
                MessageBox.Show($"Не возможно установить минимальные параметры для сканера.\n" +
                    $"Требования: RGB, DPI 300", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error);
                twain.CloseDataSource();
                return;
            }

            // Включение автоматического сканирования
            if (sAutoFeederCheckBox.IsChecked == true)
            {
                try
                {
                    twain.SetCap(TwCap.FeederEnabled, true);
                }
                catch
                {
                    MessageBox.Show("Не возможно использовать автоматическое сканирование страниц.", "Ошибка!",
                        MessageBoxButton.OK, MessageBoxImage.Error);
                    twain.CloseDataSource();
                    return;
                }

            }
            else
            {
                try
                {
                    twain.SetCap(TwCap.FeederEnabled, false);
                }
                catch { }
            }

            // Включение двухсторонего сканирования
            if (sDuplexCheckBox.IsChecked == true)
            {
                try
                {
                    twain.SetCap(TwCap.DuplexEnabled, true);
                }
                catch
                {
                    MessageBox.Show("Не возможно использовать двухсторонее сканирование страниц.", "Ошибка!",
                        MessageBoxButton.OK, MessageBoxImage.Error);
                    twain.CloseDataSource();
                    return;
                }
            }
            else
            {
                try
                {
                    twain.SetCap(TwCap.DuplexEnabled, false);
                }
                catch { }
            }

            // Запуск сканирования
            twain.Acquire();

            // Закрытие сессии
            twain.CloseDataSource();
            return;
        }

        private void twain_EndXfer(object sender, Twain32.EndXferEventArgs e)
        {
            // Получаем крайнее отсканированное изображение 
            var scannedImage = e.Image;

            // Создаём хранилище в памяти
            MemoryStream memoryStream = new MemoryStream();

            // Создаём PDF
            Document pdfDocument = new Document(new iTextSharp.text.Rectangle(scannedImage.Width, scannedImage.Height), 0, 0, 0, 0);
            PdfWriter pdfWriter = PdfWriter.GetInstance(pdfDocument, memoryStream);

            // Открываем файл
            pdfDocument.Open();

            // Добавлем изображение в PDF
            iTextSharp.text.Image pdfImage = iTextSharp.text.Image.GetInstance(scannedImage, ImageFormat.Png);
            pdfDocument.Add(pdfImage);

            // Закрываем PDF
            pdfDocument.Close();

            // Получаем байты PDF
            byte[] pdfBytes = memoryStream.ToArray();

            // Отправляем изображение на сервис
            SendFile(pdfBytes);

            // Сохраняем крайнюю страницу в файл
            //string fileName = $"C:\\Ripc\\page_{twain.ImageCount}_{DateTime.Now.ToString("MMddHHmmss")}.png";
            //e.Image.Save(fileName, ImageFormat.Png);
        }

        private void twain_AcquireError(object sender, Twain32.AcquireErrorEventArgs e)
        {
            Task.Run(() =>
            {
                var error = e.Exception.Message != "It worked!" ? e.Exception.Message : "";
                MessageBox.Show($"Ошибка при сканировании страниц.\n\n{error}", "Ошибка!",
                MessageBoxButton.OK, MessageBoxImage.Error);
            });
        }

        private void GetDevices()
        {
            // Очистка текущего списка сканеров
            sComboBox.Items.Clear();

            // Проход по найденым сканерам
            for (int i = 0; i < twain.SourcesCount; i++)
            {
                // Заполнение списка сканерами
                sComboBox.Items.Add(twain.GetSourceProductName(i));
            }

            // Проверка наличия сканеров
            if (sComboBox.Items.Count == 0)
            {
                MessageBox.Show("Сканер не подключен!", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);

                // Отключение кнопки сканирования
                startScanButton.IsEnabled = false;

                return;
            }

            // Включение кнопки сканирования
            startScanButton.IsEnabled = true;

            // Установка изначального сканера
            sComboBox.SelectedIndex = 0;

            return;
        }

        private void SetupTwain()
        {
            twain = new Twain32();

            // Отключение системного интерфейса
            twain.ShowUI = false;

            // Отключение Twain2.0
            twain.IsTwain2Enable = false;

            // Подписываемся на событие завершения сканирования страницы
            twain.EndXfer += twain_EndXfer;

            // Подписываемся на событие ошибки сканирования страницы
            twain.AcquireError += twain_AcquireError;


            if (!twain.OpenDSM())
            {
                MessageBox.Show("Сканер не подключен!", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);

                // Отключение кнопки сканирования
                startScanButton.IsEnabled = false;
                return;
            }

        }

        private void SetParametrs()
        {
            // Установка ID мероприятия на старинце
            eventIDNum.Content = parametrs[0];
        }

        private async void SendFile(byte[] file)
        {
            MultipartFormDataContent data = new MultipartFormDataContent();
            data.Add(new StringContent(parametrs[0]), "event_id");
            data.Add(new StringContent(parametrs[1]), "organization_id");
            data.Add(new ByteArrayContent(file), "byte_file", "scan.png");


            // Отправляем POST запрос на сервис
            var response = await client.PostAsync(baseURL, data);

            // Проверяем ответ
            if (!response.IsSuccessStatusCode)
            {
                MessageBox.Show("Ошибка при отправке изображения на сервер.", "Ошибка!",
                    MessageBoxButton.OK, MessageBoxImage.Error);
                // Закрытие сессии
                twain.CloseDataSource();
            }
            return;
        }

        protected override void OnClosing(CancelEventArgs e)
        {
            // Закрытие сессии twain
            twain.CloseDSM();

            base.OnClosing(e);
            return;
        }

    }
}
