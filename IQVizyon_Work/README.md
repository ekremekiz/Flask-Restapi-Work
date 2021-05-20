

Projeyi Docker İle Ayağa Kaldırmak isterseniz aşağıdaki komutları yazarak çalıştırabilirsiniz.

	docker pull ekremekiz/iqvizyon

	docker container run --name iqvizyon -p 5000:5000 ekremekiz/iqvizyon

	Not: Endpointler çalışmazsa URL'i aşağıdaki gibi değiştirmelisiniz.
	
	http://0.0.0.0:5000/app/register


Projeyi kaynak kodları ile çalıştırmak için aşağıdaki yönergeleri takip edebilirsiniz.


1. Projenin çalışabilmesi için gerekli kütüphaneler requirement.txt dosyası ile verilmiştir.

---

2. Proje app.py dosyası ile çalıştırılmaktadır.

---

3. Proje geliştirme aşamasında bütün 'GET', 'POST', 'PUT', 'DELETE' istekleri Postman uygulaması ile test edilmiştir.

---

4. Kullanıcı Kayıt İşlemi

	ÖRNEK register işlemi:

	'POST' -> /app/register

		{
    		"name":"Ekrem",
    		"email":"ekrem@ekrem.com",
    		"password":"1234"
		}

---	

5. Projede login olmadan register dışındaki hiç bir endpointe erişilemez.
	
	ÖRNEK login işlemi:

	'POST' -> /app/login

		{
			"email":"ekrem@ekrem.com",
			"password":"1234"
		}

---

6.  Logout işlemi

	'GET'-> /app/logout

	Kullanıcı oturumu sonlanır. Session sonlanır.

---

7.  @app.route('/app/users', methods=['GET', 'PUT', 'DELETE'])

	Gelen istek 'GET' ise login olmuş kullanıcının bilgilerini getirir.

	Gelen istek 'PUT' ise login olmuş kullanıcının bilgilerini günceller.

	ÖRNEK Kullanıcı Güncelleme

		{
    		"name":"EkremEkiz",
    		"email":"ekremekiz@ekrem.com",
    		"password":"12345"
		}
	
	Gelen istek 'DELETE' ise login olmuş kullanıcıyı siler ve logout işlemi gerçekleşir. Session Sonlanır.

---

8. @app.route('/app/boards', methods=['GET', 'POST'])

	Gelen istek 'GET' ise login olmuş kullanıcının erişebileceği iş kayıtlarını getirir.

	Gelen istek 'POST' ise login olmuş kullanıcı yeni bir iş kaydı ekler.

	ÖRNEK 'POST' isteği:

		{
			"name": "Board1",
        	"status": "Aktif"
		}

	NOT: Tanımlanmış olan STATUS_BOARD Tuple ile iş kaydı sırasında status bilgisinin Aktif veya Arşivlenmiş dışında bir değer girilmesi engellenmiştir.

---

9. @app.route('/app/boards/<board_id>', methods=['GET', 'PUT', 'DELETE'])

	NOT: Session kontrolü ile kullanıcın kendisi tarafından oluşturulmamış iş kayıtlarını görmesi, güncellemesi ve silmesi engellenmiştir.

	Gelen istek 'GET' ise Id'si gönderilen iş kaydı detayları gösterilir.

	Gelen istek 'PUT' ise Id'si gönderilen iş kaydı güncellenir.

	ÖRNEK 'PUT' İsteği:

		{
			"name": "BoardUpdate",
        	"status": "Aktif"
		}
	
	Gelen istek 'DELETE' ise Id'si gönderilen iş kaydı silinir.

---

10. @app.route('/app/user_active_boards', methods=['GET'])

	Kullanıcı Başarılı şekilde Login olduğunda durumu aktif olan iş kayıtları listelenir. Bu istek Login işlemi sırasında tetiklenir.

---

11. @app.route('/app/cards', methods=['GET', 'POST'])

	Gelen istek 'GET' ise giriş yapmış kullanıcının görmeye yetkili olduğu kartlar listelenir.

	Gelen istek 'POST' ise kullanıcı yeni bir kart ekler.

	ÖRNEK 'POST' işlemi:

		{
			"title":"Card1",
    		"content":"Card1",
    		"status":"Başladı",
    		"assignee":["168aa0f2-02bd-4c3c-8d77-682a1ba9a3e4"],
    		"start_date":"2021-05-19",
    		"due_date":"2021-05-20"
		}

---

12. @app.route('/app/cards/<card_id>', methods=['GET', 'PUT', 'DELETE'])

	NOT: Session kontrolü ile kullanıcın erişim yetkisi olmayan kartları görmesi, güncellemesi ve silmesi engellenmiştir.

	Gelen istek 'GET' ise Id'si gönderilen kart detayları gösterilir.

	Gelen istek 'PUT' ise Id'si gönderilen kart güncellenir.

	ÖRNEK 'PUT' İsteği:

		{
			"title":"Card1",
    		"content":"Card1",
    		"status":"Başladı",
    		"assignee":["168aa0f2-02bd-4c3c-8d77-682a1ba9a3e4"],
    		"start_date":"2021-05-19",
    		"due_date":"2021-05-20"
		}
	
	Gelen istek 'DELETE' ise Id'si gönderilen kart silinir.

---

13. @app.route('/app/comments', methods=['GET', 'POST'])

	Gelen istek 'GET' ise giriş yapmış kullanıcının görmeye yetkili olduğu yorumlar listelenir.

	Gelen istek 'POST' ise kullanıcı karta yeni bir yorum ekler.

	ÖRNEK 'POST' işlemi:

		{
			"content":"Commend16",
    		"created_by":"9d85f9fd-b754-4e7d-8249-098926d958af",
    		"card":"97f0c970-040b-4e93-a7ff-a129b4c07e1d"
		}

14. @app.route('/app/comments/<comment_id>', methods=['GET', 'PUT', 'DELETE'])

	NOT: Session kontrolü ile kullanıcın erişim yetkisi olmayan yorumları görmesi, güncellemesi ve silmesi engellenmiştir.

	Gelen istek 'GET' ise Id'si gönderilen yorum detayları gösterilir.

	Gelen istek 'PUT' ise Id'si gönderilen yorum güncellenir.

	ÖRNEK 'PUT' İsteği:

		{
			"content":"Commend16"
		}
	
	Gelen istek 'DELETE' ise Id'si gönderilen yorum silinir.

---

15. @app.route('/app/card_comments/<card_id>', methods=['GET'])

	Bu endpoint ile Id'si gönderilen karta ait olan yorumlar listelenir.

	Session kontrolü ile kullanıcının kartı görmeye yetkisi yoksa kartın yorumları da gösterilmez.

---

NOT: Veri tabanı erişimi için MongoDB Atlas email ve şifre bilgisi mail ile paylaşılmıştır.







	






	




	


